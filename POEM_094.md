POEM ID: 094  
Title: Driver Autoscaling and Refactor.   
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  N/A  
Associated implementation PR: N/A. 

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted 
- [ ] Rejected
- [ ] Integrated

## Motivation

OpenMDAO currently requires users provide manual scaling for their optimization problems, or use the autoscaling
options in IPOPT.

Since IPOPT has limited options for this and not all users use IPOPT, it makes sense to have OpenMDAO provide _some_ autoscaling capability in an extensible manner.

No autoscaling algorithm works for all use-cases, but if we can ease the burden for some users by providing this capability it seems like it may be worthwhile.

## Proposed Solution

This POEM consists of a few thrusts.

### We will refactor the Driver class to implement `OptimizationDriver` and `AnalysisDriver`.

`OptimizationDriver` will be associated with optmization and will support some methods that just don't make sense in an Analysis standpoint. This will be the parent class for `ScipyOptimizeDriver`, `pyOptSparseDriver`, `SimpleGADriver`, and `DifferentialEvolutionDriver`.

`AnalysisDriver` will support design exploration, but the notion of scaling doesn't apply here.

- AnalysisDriver will allow changes to any variable, and potentially provide all inputs to `set_val` (for each name, provide an associated `val`, with optional `units`, and `indices`).
- Different ways of providing run points to AnalysisDriver will dictate if it acts like a run-once driver, a DOE driver, a monte-carlo driver, etc.
- AnalysisDriver will have a recorder attached by default.
- Drivers will support `add_constraint`, `add_objective`, and `add_design_var` (just passed through to apply to the underlying model.)
- AnalysisDriver will support `add_response`, an output to be recorded but the notion of a constraint or objective doesn't really make sense in the context.
- AnalysisDriver will record all design vars, constraints, objectives, responses by default - those are probably what the user is keen in recording.

### Driver runs will return a DriverResults object.

The current return value of `failed` doesn't provide any information on the optimization and forces the user to go digging through the optimizers to find things like iteration counts, informs/exit status, Lagrange multipliers, etc.

In addition, the users find the notion that a successful optimization returns a value of `False` to be confusing.

This proposal will change the return value of a driver run to a new type called `DriverResults`.

Any aspect that we expect to be common across several drivers should be an attribute/property of `DriverResults`.

This will include:
- `success`: Flag that is `True` if the optimization was successful.
- `message`: The driver-specific exit message.
- `model_evals`: The number of executions of model.solve_nonlinear()
- `model_time`: Time spent evaluating model.solve_nonlinear()
- `deriv_evals`: The number of executions of compute_totals.
- `deriv_time`: Time spent executing compute_totals.

`DriverResults` will contain an attribute/property `success` that is a boolean indicating whether the driver successfully ended.  The meaning of this flag will vary from driver to driver (and optimizer to optmizer).  For instance, SLSQP has a rather straight-forward success criteria, while SNOPT has multiple inform results that might indicate success.

**Note: These changes are backwards incompatible and will impact anyone who is checking the return value of `run_driver`,
since this object (as most Python objects), will evaluate to `True`.

### OptimizationDrivers will support the notion of an `Autoscaler` that is called early in their `run`. The autoscaler will be set using `driver.set_autoscaler(AutoscalerClass())`.

### OpenMDAO will provide some default set of Autoscalers (discussed below), and allow users to implement their own.

## Changes to OptimizationDriver

### Autoscaling Changes

 - `Driver.add_autoscaler(Autoscaler())` will be used to add autoscalers to the driver.
 - Autoscalers will be run in sequence, so autoscaling algorithms that only apply to certain systems in the model can be responsible for setting their scaling factors.
 - The autoscaler will default to None, which results in the current behavior of manual scaling only.
 - `Driver._setup_driver` will set `has_scaling` to True if the current condition is True *OR* it has one or more autoscalers.
 - `Driver.run` will call the autoscaling algorithms before run_case. It will set `total_scaler` and `total_adder` for the dvs, cons, and objectives.

### New Methods

- `_find_feasible` 🟢

Use a least-squares solver to minimize the constraint violations. 

- `compute_lagrange_multipliers` 🟢

Get the lagrange multipliers for optimizers which provide them, in an optimizer-independent way. This will be useful for evaluating post-optimality sensititivity.

- `compute_post_optimality_sensitivities` 🔴

Provide the sensitivities/derivatives of the objective and design variable values _across_ the optimization.
The sensitivities of design variable changes will require computing or approximating second derivatives.

## Autoscale API 🟡

Autoscaler will provide various `scale` methods.  Note that in OpenMDAO, the general nomenclature is that the
model values are _unscaled_ and the corresponding optimizer values are _scaled_.

```
def unscale_desvars(self, driver):
    """
    Scale the design variables from the optimizer space to the model space.


    This will be called at every iteration and should therefore be as efficient as possible. Several implementations
    of autoscaling effectively compute it as "x_model = M @ x_optimizer". In large problems, M will need to be sparse
    or be a linear operator to save memory.
    """
```

```
def scale_desvars(self, driver):
    """
    Scale the design variables from the model space to the optimizer space.

    This will be called to initialize the optimizers design variable vector.

    In the previous example, this would effectively apply "x_optimizer = M^{-1} @ x_model
    """
```

```
def scale_cons(self, driver):
    """
    Used in get_constraint_values, provides a scaling function that converts the model constraint values
    to the optimizer space.
    """
```

```
def scale_objs(self, driver):
   """
   Used in get_objective_values, provides a scaling function that converts the model-space objective values
   to the optimizer space.
   """
```

```
def setup(self, driver):
    """
    Called when the driver is being setup, this should be used to provide scaling based on the initial state of the model.
    """
```

Problem provides access to both the model and the driver, so we can interrogate things like optimizer settings.
The other arguments are output dictionaries each keyed by the desvar, constraint, or objective name.
For each key in these dictionaries, the user can provide the scaler, adder, ref, or ref0.

```
# scale x by dividing by it's initial value
x_val = problem.get_val('x')
desvar_scaling['x']['scaler'] = 1 / x_val
```

## Proposed Initial Autoscalers

### `DefaultAutoscaler`

DefaultAutoscaler will use the `total_scaler` information from design variables, optimizers, and constraints and apply that.
Equivalent to existing OpenMDAO behavior, but implemented in a more general way.

For example, unscale_desvars could be implemented as `x_model = [total_scaler]^{-1} @ x_optimizer - [total_adder]` where `[total_scaler]` is a matrix with the total scaler of each design variable on its diagonal.

**Other autoscalers should probably include the option to use/disregard any scaling that the user has placed on individual design variables and responses, but all will need to take into 
account any unit-conversions defined when the design variables or responses were added.**

### `SimpleAutoscaler`

SimpleAutoscaler will enforce that the design variable vector is scaled to have a norm of approximately 1.0.
If users impose scaler/adder or ref0/ref scaling on their design variables, those will be assumed to be the correct scalers.
Otherwise, if scaler/adder/ref/ref0 are `None`, DefaultAutoscaler use the reciprocal of the initial value as the scaler if it's absolute value is greater than one, otherwise it will use ref0=-1, ref=1.

Constraints will have a option, autoscale_tolerance, which will default to 1.0E-3. This specifies the number of decimal places to which the constraint should be satisfied. The scale factor can then be computed from this as `scaler = autoscale_tolerance / feasibility_tolerance`.

If a specific driver used does not support the notion of feasibility tolerance, raise an error so that this Autoscaler may not be used.

### `HessianAutoScaler`

Provides scaling based on the work of Habeeb Idris and Prof. Jason Hicken [Reference](https://arc.aiaa.org/doi/epdf/10.2514/6.2025-3738)

### `PJRNAutoscaler`

 Projected Jacobian Row Norm scaling algorithm
 [Reference](https://elib.dlr.de/93327/1/Performance_analysis_of_linear_and_nonlinear_techniques.pdf)
 
 This scaler will require that bounds be set on all design variables.
 This scaler will use the values of `lower` and `upper` as `ref0` and `ref`, and compute the corresponding `scaler` and `adder` values.
 The `scaler` is `1 / K_x` as referenced by the paper, and adder is `b_x`.
