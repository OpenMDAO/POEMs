POEM ID: 068  
Title:  Nonlinear Solver State Caching  
authors: @lamkina  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: (not submitted yet)  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated



## Motivation

Many optimizers employ backtracking algorithms to recover from failed model evaluations.
After a failed evaluation, the user in conjunction with OpenMDAO must decide how to initialize the model's states
for the next backtracking iteration.  Three main options exist:

1. **Cold Start:**  Use the initial guesses to the model at the onset of the optimization problem.
2. **Warm Start:**  Use the final states from the previous optimization iteration.
3. **Restart**:  Use cached states from the last successful model evaluation.

Currently, OpenMDAO relies on the *warm start* method because in general it behaves well for consecutive
successful model evaluations. However, models that rely on nonlinear solvers to resolve implicit
relationships are vulnerable to a number of failure cases that break the warm start approach during
backtracking.

For example, a residual equation in the model may involve a `log` function that depends on a state
of the nonlinear system.  Certain design variable combinations can cause an iterative solver towards a negative value
for this state, therefore raising an `AnalysisError`.  If the optimizer attempts to backtrack from the failed
evaluation, but warm starts the solver using the bad negative state, the `log` function will once again fail.
In this scenario, often seen in propulsion modeling due to chemical equilibrium analysis equations, the optimizer
enters an indefinite fail loop and eventually exits.

OpenMDAO can avoid this outcome using the *restart* method because in the backtracking iteration, cached states
from a previous successful model solution are used as initial guesses to the nonlinear system.  In theory,
the previous successful solution should be the current point, and as the backtracking steps approach this point,
the cached states become an increasingly better initial guess for the nonlinear solver.

## Description

### Summary

This POEM implements the *restart* method using system output caching in the nonlinear solver base class. A
reference implementation can be found [here](https://github.com/lamkina/OpenMDAO/blob/solver_cache/openmdao/solvers/solver.py).

The premise behind the method is as follows:

1. After a successful model evaluation involving a nonlinear solver, cache the system output vector.
2. If the model fails to converge in a subsequent iteration, set a *previous evaluation fail flag* to true.
3. Upon the next model evaluation, replace the current system outputs with the cached outputs before running
   the nonlinear solver.
4. Evaluate the model with the cached outputs as the initial guess for the nonlinear system.

The caching feature will exist within the `NonlinearSolver` base class and work synergistically with the MAUD framework by only caching states at or below the current system.  Additionally, users will only see one change to the nonlinear solver interface, making this feature easy to learn and add to new and existing models.

### Changes to the Nonlinear Solver Interface

The addition of system output caching introduces a change to user interaction with the nonlinear solver interface.

- The user can set a new option `use_cached_states=True` to enable the system output cache feature.

> **_NOTE:_** The `use_cached_states` option only works when `err_on_non_converge=True` because it needs to set the fail flag when an `AnalysisError` is thrown by the solver exit conditions.

Here is an example of a nonlinear solver setup with this new option:

```python
solver = self.nonlinear_solver = om.NewtonSolver(solve_subsystems=True)
solver.options["use_cached_states"] = True
solver.options["err_on_non_converge"] = True
```

### Reference Implementation

The system output cache only requires changes to the `NonlinearSolver` base class. The
first change is adding a `_prev_fail` attribute to record when the solver will require a
restart on the next optimization iteration.

```python
def __init__(self, **kwargs):
    """
    Initialize all attributes.
    """
    super().__init__(**kwargs)
    self._err_cache = OrderedDict()
    self._state_cache = OrderedDict()
    self._prev_fail = False
```


The second change involves adding the `use_cached_states` option in the `_declare_options` method:

```python
def _declare_options(self):
    """
    Declare options before kwargs are processed in the init method.
    """
    self.options.declare(
        "debug_print",
        types=bool,
        default=False,
        desc="If true, the values of input and output variables at "
        "the start of iteration are printed and written to a file "
        "after a failure to converge.",
    )
    self.options.declare(
        "stall_limit",
        default=0,
        desc="Number of iterations after which, if the residual norms are "
        "identical within the stall_tol, then terminate as if max "
        "iterations were reached. Default is 0, which disables this "
        "feature.",
    )
    self.options.declare(
        "stall_tol",
        default=1e-12,
        desc="When stall checking is enabled, the threshold below which the "
        "residual norm is considered unchanged.",
    )
    self.options.declare(
       "use_cached_states",
       types=bool,
       default=False,
       desc="If true, the states are cached after a successful solve and "
       "used to restart the solver in the case of a failed solve.",
    )
```

The remaining changes occur in the `solve` method:

```python
def solve(self):
    """
    Run the solver.
    """
    # The state caching only works if we throw an error on non-convergence, otherwise
    # the solver will disregard the state caching options and throw a warning.
    if self.options["use_cached_states"] and not self.options["err_on_non_converge"]:
        msg = "Caching states does nothing unless option 'err_on_non_converge' is set to 'True'"
        issue_warning(msg, category=SolverWarning)

    # Get the system for this solver
    system = self._system()
    try:

        # print(system._subsystems_allprocs)
        # If we have a previous solver failure, we want to replace
        # the states using the cache.
        if self._prev_fail and self.options["use_cached_states"]:
            system._outputs.set_vec(self._state_cache["outputs"])

        # Run the solver
        self._solve()

        # If we make it here, the solver didn't throw an exception so there
        # was either convergence or a stall.  Either way, the solver didn't
        # fail so we can set the flag to False.
        if (
            self.options["use_cached_states"]
            and not system.under_complex_step
            and not system.under_finite_difference
            and not system.under_approx
        ):
            self._prev_fail = False

            # Save the states upon a successful solve
            self._state_cache["outputs"] = deepcopy(system._outputs)

    except Exception as err:
        # The solver failed so we need to set the flag to True
        self._prev_fail = True

        if self.options["debug_print"]:
            self._print_exc_debug_info()
        raise err
```

> **_NOTE:_** Until a PR is submitted, the full reference implementation is located [here](https://github.com/lamkina/OpenMDAO/blob/solver_cache/openmdao/solvers/solver.py).

### Example Scripts

Two example scripts are provided to demonstrate the functionality of this feature.

1. Simple 3 component implicit model: `POEM_068/test_1.py`
2. High bypass turbofan pyCycle model: `POEM_068/test_2.py`

### Discussion Topics

1. How will this feature interact with `guess_nonlinear`?
   - Currently, `guess_nonlinear` is called after the solver restart.  This means the `guess_nonlinear` function will operate on the cached outputs after a restart occurs.  I think this makes the most sense because in a majority of cases the user will not want to run `guess_nonlinear` on states that cause underlying functions to fail in the first place.
   - If the `use_cached_states` option is `False`, `guess_nonlinear` will not be affected and OpenMDAO will use the *warm start* method as expected.
2. Is any additional logic necessary to prevent unwanted behavior with this feature?
   - Things I've included:
     - Don't use this feature while the system is under complex step, approximation, or finite differencing.
     - Check to make sure `err_on_non_converge` is `True` and throw a `SolverWarning` with an informative message if it's `False`.
     - Set a flag to track solver failures in previous iterations to initiate a restart on the following model evaluation.
