POEM ID: 094  
Title: Driver Autoscaling and Refactor.   
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  N/A  
Associated implementation PR: N/A. 

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [ ] Integrated

## Motivation

OpenMDAO currently requires users provide manual scaling for their optimization problems, or use the autoscaling
options in IPOPT.

Since IPOPT has limited options for this and not all users use IPOPT, it makes sense to have OpenMDAO provide _some_ autoscaling capability in an extensible manner.

No autoscaling algorithm works for all use-cases, but if we can ease the burden for some users by providing this capability it seems like it may be worthwhile.

## Proposed Solution

This POEM consists of a few thrusts.

1. We will refactor the Driver class to implement `OptimizationDriver` and `AnalysisDriver`.

`OptimizationDriver` will be associated with optmization and will support some methods that just don't make sense in an Analysis standpoint. This will be the parent class for `ScipyOptimizeDriver`, `pyOptSparseDriver`, `SimpleGADriver`, and `DifferentialEvolutionDriver`.

`AnalysisDriver` will support design exploration, but the notion of scaling doesn't apply here, as this driver will not support objectives or constraints, but just "responses". This will be the parent class for `DOEDriver`.

2. OptimizationDrivers will support the notion of an `Autoscaler` that is called early in their `run`. The autoscaler will be set using `driver.set_autoscaler(AutoscalerClass())`.

3. OpenMDAO will provide some default set of Autoscalers (discussed below), and allow users to implement their own.

## Changes to OptimizationDriver

### Autoscaling Changes

 - `Driver.add_autoscaler(Autoscaler())` will be used to add autoscalers to the driver.
 - Autoscalers will be run in sequence, so autoscaling algorithms that only apply to certain systems in the model can be responsible for setting their scaling factors.
 - The autoscaler will default to None, which results in the current behavior of manual scaling only.
 - `Driver._setup_driver` will set `has_scaling` to True if the current condition is True *OR* it has one or more autoscalers.
 - `Driver.run` will call the autoscaling algorithms before run_case. It will set `total_scaler` and `total_adder` for the dvs, cons, and objectives.

### New Methods

- `get_feasibility_tol`

Return the current feasibility tolerance for the optimizer. This provides a consistent optimizer-independent way of getting the feasibility tolerance for optimizers which support this concept. This is useful for scaling and potentially working out the active set of constraints from the OpenMDAO side of things. This can be obtained as option `Major Feasilibity Tol` from SNOPT or `constraint_viol_tol` from IPOPT, for instance.

- `get_lagrange_multipliers`

Get the lagrange multipliers for optimizers which provide them, in an optimizer-independent way. This will be useful for evaluating post-optimality sensititivity.

## Autoscale API

Autoscaler will provide a `scale` method with a signaiture

```
def scale(problem, desvar_scaling, constraint_scaling, objective_scaling)
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

### `SimpleAutoscaler`

SimpleAutoscaler will enforce that the design variable vector is scaled to have a norm of approximately 1.0.
If users impose scaler/adder or ref0/ref scaling on their design variables, those will be assumed to be the correct scalers.
Otherwise, if scaler/adder/ref/ref0 are `None`, DefaultAutoscaler use the reciprocal of the initial value as the scaler if it's absolute value is greater than one, otherwise it will use ref0=-1, ref=1.

Constraints will have a option, autoscale_tolerance, which will default to 1.0E-3. This specifies the number of decimal places to which the constraint should be satisfied. The scale factor can then be computed from this as `scaler = autoscale_tolerance / feasibility_tolerance`.

If a specific driver used does not support the notion of feasibility tolerance, raise an error so that this Autoscaler may not be used.

### `PJRNAutoscaler`

 Projected Jacobian Row Norm scaling algorithm
 [Reference](https://elib.dlr.de/93327/1/Performance_analysis_of_linear_and_nonlinear_techniques.pdf)
 
 This scaler will require that bounds be set on all design variables.
 This scaler will use the values of `lower` and `upper` as `ref0` and `ref`, and compute the corresponding `scaler` and `adder` values.
 The `scaler` is `1 / K_x` as referenced by the paper, and adder is `b_x`.
