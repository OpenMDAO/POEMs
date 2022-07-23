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

This POEM implements the *restart* method using cached states within the nonlinear solver.



