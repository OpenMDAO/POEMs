POEM ID: 061  
Title: The `openmdao:allow_desvar` tag  
authors: @robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2350](https://github.com/OpenMDAO/OpenMDAO/pull/2350)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

Currently a user can assign any output as a design variable, though this is almost certainly unwanted behavior.
Still, the possibility exists that a user may wish to create an IndepVarComp-like component of their own, so we cannot simply disallow design variables on all non IVC outputs.

```
import openmdao.api as om

prob = om.Problem()
root = prob.model

prob.driver = om.ScipyOptimizeDriver()

root.add_subsystem('initial_comp', om.ExecComp(['x = 10']), promotes_outputs=['x'])

outer_group = root.add_subsystem('outer_group', om.Group(), promotes_inputs=['x'])
inner_group = outer_group.add_subsystem('inner_group', om.Group(), promotes_inputs=['x'])

c1 = inner_group.add_subsystem('c1', om.ExecComp(['y = x * 2.0',  'z = x ** 2']),  promotes_inputs=['x'])

c1.add_design_var('x', lower=0, upper=5)
c1.add_constraint('y', lower=1.5)
c1.add_objective('z')

prob.setup()

prob.run_driver()
prob.list_problem_vars()
```

## Solution

To get around this, we will create a new tag: `openmdao:allow_desvar`, and any attempt to assign a design variable to an output _without_ this tag will result in an exception be raised.

By default, this tag will be applied to outputs of
- IndepVarComp
- ImplicitComponent

Checking whether a variable can be validly made a design variable is then just a matter of testing if it has this tag applied to it.

In the rare corner case that a user implements their own IndepVarComp-like component, they will be able to tag outputs to allow them to be design variables.
