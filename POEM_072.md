POEM ID: 072  
Title: Add ability to modify bounds and scaling of implicit outputs and optimizer variables after creation.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: OpenMDAO/OpenMDAO#2731  


Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

In OpenMDAO, implicit outputs can have bounds attach to them that are enforced by bounds-enforcing linesearches within nonlinear solvers.
These bounds are defined when `add_output` is called on an implicit component.

In complex models, this means that a user may need to tweak bounds in multiple files.
The bounds of a variable may be dependent upon the application of the model.
These bounds may need to be adjusted in a file that is generally outside of the expertise of the user.

Instead, we should take an approach that:
- allows users to set bounds throughout their model from a single script or notebook.
- avoids inadvertent git commits that change the model in order to be applicable to the current application.

## What properties of outputs should the user be able to edit outside of the component?

Users should _not_ be able to change variable metadata that affects `compute`, `compute_partials`, or `apply_linear` within a component.
The internal methods to a component assume a certain set of units, certain shapes, etc.
So the method we use for adjusting bounds should not be a generic "set_metadata" method.

We should limit the user to changing properties associated with the nonlinear solver: `lower`, `upper`, `ref`, `ref0`, `res_ref`.  I'm currently undecided if we need to give the user the ability to change tags.

When used, OpenMDAO should check, at a minimum, that the given path is a valid output.

## Proposed API for Outputs

```python

prob.model.set_output_solver_options(name='path.to.output', lower=_unspecified, upper=_unspecified, ref=_unspecified, ref0=_unspecified, res_ref=_unspecified)

```

Any of the arguments which are not `_unspecified` will be overridden in the outputs metadata.

# What about optimizers?

The same rationale for changing bounds/scaling output variables within solvers exists for optimizer design variables, constraints, and objectives.
We should support modifying things like desvar and constraint bounds and scaling, and objective scaling.

## Proposed API for optimizer desvars, constraints, and objectives

OpenMDAO's `add_design_var`, `add_constraint`, and `add_objective` imply that a new desvar, constraint, objective is being created.
The new API should allow properties of those already created to be modified in place:

```python
prob.model.set_design_var_options('path.to.desvar', equals=_unspecified, lower=_unspecified, upper=_unspecified, scaler=_unspecified, adder=_unspecified, ref=_unspecified, ref0=_unspecified)
prob.model.set_constraint_options('alias' or 'path.to.con', equals=_unspecified, lower=_unspecified, upper=_unspecified, scaler=_unspecified, adder=_unspecified, ref=_unspecified, ref0=_unspecified)
prob.model.set_objective_options('path.to.obj', scaler=_unspecified, adder=_unspecified, ref=_unspecified, ref0=_unspecified)
```

One complication is the path to constraints in `set_constraint_options`, since a single variable may have multiple constraints imposed upon it provided they are aliased, but we should be able to account for this.  If there is ambiguity (an alias exists), raise an error.

Note that we can arrive at a situation in which, if we're redefining `scaler/adder/ref0/ref`, where all 4 are specified. If the user overrides any of these, the others should be reset to `None`.

The function names in this POEM are up for debate.

