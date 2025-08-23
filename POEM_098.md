POEM ID: 098  
Title: Automatic association of solvers to cycles.  
authors: naylor-b (Bret Naylor)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#3292](https://github.com/OpenMDAO/OpenMDAO/pull/3292)  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

OpenMDAO currently uses Groups for two purposes.  The first is to provide a namespace that applies
to all subsystems and variables found beneath that group in the system tree.  The second is to
provide a location in the system tree where nonlinear and linear solvers can be used to iterate
over that portion of the system tree.

It is sometimes desirable to create groups with names that logically correspond to the physical 
systems being modeled or to another layout that will be more intuitive for users. This layout may 
lead to some groups containing subsystems that form cycles due to data dependencies, while others do not.

In the current version of OpenMDAO, iterative nonlinear and linear solvers must be associated with 
the entire group, even if only the cycle within the group requires them. Placing the solvers at the 
group level above the cycle can lead to unnecessary execution of the non-cycle subsystems.


## Proposed solution

We propose to create a new type of Group called `CycleGroup`, that lives in the system tree like
other Groups but does not act as a namespace, meaning that `CycleGroup`'s name will not appear in
any absolute or promoted name of any system or variable it contains. `CycleGroup`'s only purpose
is to use solvers to iterate over its subsystems.

Instead of adding solvers to the original Group that contains the sub-cycle, the user would call
`add_subsolvers` on the original Group, for example,


```grp.add_subsolvers(nonlinear_solver=om.NonlinearBlockGS(maxiter=100), linear_solver=om.LinearBlockGS(maxiter=100), cycle_system=<subsystem_name>) ```


where `<subsystem_name>` is the name of any subsystem that belongs to the sub-cycle of interest.


During OpenMDAO's setup process, just after all data connections are known, any Group where 
`add_subsolvers` has been called will compute its subsystem dependency graph and identify any cycles.
If a `<subsystem_name>` provided to the `add_subsolvers` call is found in a given cycle, then a 
`CycleGroup` is created and added to the parent Group.  All subsystems of the parent Group that 
are in the cycle are moved from the parent Group down into the `CycleGroup`.  Finally, certain 
data structures in the `CycleGroup` are initialized based on those in the parent Group.


## Example

In the following example, the group 'G1' contains a cycle ['d1', 'd2'], and a number of subsystems
that are not in a cycle, e.g., 'obj_comp', 'con_cmp1' and 'con_cmp2'.  To prevent unnecessary 
iteration of 'obj_comp', 'con_cmp1' and 'con_cmp2', we want to associate solvers with only the
cycle subsystems 'd1', and 'd2'.  To do this, we call `add_subsolvers` on 'G1', telling it to use
nonlinear and linear block Gauss-Seidel solvers, and pass 'd1' as the cycle_system arg.  We could
have passed 'd2' instead and it would work in the same way as with 'd1'.


```python
    p = om.Problem()
    model = p.model
    G1 = model.add_subsystem('G1', om.Group(), promotes=['*'])
    G1.add_subsystem('d1', dis1(), promotes=['x', 'z', 'y1', 'y2'])
    G1.add_subsystem('d2', dis2(), promotes=['z', 'y1', 'y2'])

    G1.add_subsystem('obj_cmp', om.ExecComp('obj = x**2 + z[1] + y1 + exp(-y2)',
                                            z=np.array([0.0, 0.0]), x=0.0),
                     promotes=['x', 'z', 'y1', 'y2', 'obj'])

    G1.add_subsystem('con_cmp1', om.ExecComp('con1 = 3.16 - y1'), promotes=['con1', 'y1'])
    G1.add_subsystem('con_cmp2', om.ExecComp('con2 = y2 - 24.0'), promotes=['con2', 'y2'])

    G1.add_subsolvers(om.NonlinearBlockGS(maxiter=100), om.LinearBlockGS(maxiter=100), 'd1')

    p.setup()
    p.run_model()
```
