POEM ID: 099  
Title: InputResidsComp  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#3295](https://github.com/OpenMDAO/OpenMDAO/pull/3295)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation

A while ago, OpenMDAO added the capability to allow implicit components to have differing numbers of residual variables and outputs, so long as the total size of the residuals is equal to the total size of the outputs ([POEM_069](https://github.com/OpenMDAO/POEMs/blob/master/POEM_069.md)).

Since then, one pattern that seemed to recur as a result of this change was to create an ImplicitComponent that simply took any input given and used it as a residual value for the system.

Rather than reimplementing this capability repeatedly, the decision has been made to add it as an OpenMDAO component.

## Proposed Solution

`InputResidsComp` is an ImplicitComponent for which overrides `add_input`, allowing a residual ref value to be provided in addition to the typical input metadata.

Implicit outputs are added with the `add_output` method. **They are not added automatically** as they are with something like the `BalanceComp`.

## Required Changes to OpenMDAO

OpenMDAO currently allows inputs and outputs to be shaped based upon connections or relative to other inputs and outputs through `shape_by_conn`, `copy_shape`, and `compute_shape` areguments. Residuals do not currently support these arguments.

This is similar to the issues that drove the need for a `setup_partials` method which allowed partials to be declared in `final_setup`, once the sizes of all inputs and outputs ad been resolved.

As of a result, OpenMDAO components will get a `setup_residuals` method which will allow `add_residual` to be called once sizes have been resolved.

- It is an error to define `setup_residuals` in an ExplicitComponent

## Example

The following example shows how `InputResidsComp` can be used in a situation where the number of inputs/residuals and outputs differ, but their total sizes are the same.

```python
def test_input_resids_comp_copy_shape(self):
    p = om.Problem()

    p.model.add_subsystem('exec_comp',
                            om.ExecComp(['res_a = a - x[0]',
                                        'res_b = b - x[1:]'],
                                        a={'shape': (1,)},
                                        b={'shape': (2,)},
                                        res_a={'shape': (1,)},
                                        res_b={'shape': (2,)},
                                        x={'shape':3}),
                                        promotes_inputs=['*'],
                                        promotes_outputs=['*'])

    resid_comp = p.model.add_subsystem('resid_comp',
                                        om.InputResidsComp(),
                                        promotes_inputs=['*'],
                                        promotes_outputs=['*'])

    resid_comp.add_output('x', shape=(3,))
    resid_comp.add_input('res_a', shape_by_conn=True, ref=1.0)
    resid_comp.add_input('res_b', shape_by_conn=True, ref=1.0)

    p.model.nonlinear_solver = om.NewtonSolver(solve_subsystems=False)
    p.model.linear_solver = om.DirectSolver()

    p.setup()

    p.set_val('a', 3.0)
    p.set_val('b', [4.0, 5.0])

    p.run_model()
```
