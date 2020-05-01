POEM ID:  008  
Title:   Nonlinear Solver Refactor  
authors: [DKilkenny] (Danny Kilkenny)    
Competing POEMs: [N/A]  
Related POEMs: [N/A]  
Associated Implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1157  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

This POEM covers two changes to the nonlinear solvers:

Feedback from the 2019 OpenMDAO Workshop indicated that the `solve_subsystems` option on any solver 
should be a requirement for the user to set either as an argument or setting the option
independently. 

The second part of this POEM was feedback from Eliot Aretskin-Hariton (NASA). This feedback was to create a new option for nonlinear solvers to reraise any AnalysisError 
that might arise during a subsolve.

Description
-----------

The examples below show how the new functionality would be for setting `solve_subsystems` through 
the constructor and independently setting the option. 

**Note**: This is not a backward compatible API change 

 
```
def solve_subsystems_example():
    """ Setting solve_subsystems through the constructor """

    prob = om.Problem()
    nlsolver = om.NewtonSolver(solve_subsystems=False)
    prob.model = SellarDerivatives(nonlinear_solver=nlsolver,
                                   linear_solver=om.LinearBlockGS())
    
    prob.setup()
    prob.run_model()
```

```
def solve_subsystems_example():
    """ Setting solve_subsystems independently with options """

    prob = om.Problem()
    nlsolver = om.NewtonSolver()
    prob.model = SellarDerivatives(nonlinear_solver=nlsolver,
                                   linear_solver=om.LinearBlockGS())

    nlsolver.options['solve_subsystems'] = False
    
    prob.setup()
    prob.run_model()
```

A user can have a model with a subsolver which may not converge and raises an `AnalysisError`. If the optimizer is capable of stepping back and trying again with a safer point, it will do that. However, only the top solver knows if your whole model has failed to converge. The subsolver may reach the maximum number of iterations on an early iteration of the top solver. When using a capable optimizer, the top level solver can update with a new point which may allow the subsolver to converge. In this case, it would be helpful to supress the error so the solver can have a change to converge instead of being stopped early.

The current implementation will raise an error if the subsolver fails to converge at any time when `err_on_non_converge` is set to `True`. The new proposed implementation would provide a new option `reraise_child_analysiserror` which, when set to true, will raise the error just like before and when set to false, it will supress the AnalysisError to allow the subsolver to update.

Below we have an example of the new functionality. 

```
def reraise_child_analysiserror_example():
    # Raises AnalysisError when run

    prob = om.Problem(model=DoubleSellar())
    model = prob.model

    g1 = model.g1
    g1.nonlinear_solver = om.NewtonSolver()
    g1.nonlinear_solver.options['maxiter'] = 1
    g1.nonlinear_solver.options['err_on_non_converge'] = True
    g1.nonlinear_solver.options['solve_subsystems'] = True
    g1.linear_solver = om.DirectSolver(assemble_jac=True)

    model.nonlinear_solver = om.NewtonSolver()
    model.linear_solver = om.ScipyKrylov(assemble_jac=True)
    model.nonlinear_solver.options['solve_subsystems'] = True
    # To hide the error, change this to False or remove the line all together. The default is False.
    model.nonlinear_solver.options['reraise_child_analysiserror'] = True

    prob.setup()

    prob.run_model()
```
