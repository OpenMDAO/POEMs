POEM ID: 090  
Title: Auto ordering of Group subsystems.  
authors: naylor-b (Bret Naylor)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [PR 2963](https://github.com/OpenMDAO/OpenMDAO/pull/2963)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [x] Integrated

## Motivation

Subsystem execution order within a Group is currently set in one of two ways.  Calling the `set_order` method will
specify the order.  Otherwise, the order that subsystems were added to a Group determines their order. In either case,
there is no guarantee that the subsystems will execute in proper data flow order. As models become more complex it's not
always easy to determine the proper dataflow order, and if data flow order is violated then convergence issues may result.


## Proposed Solution

This POEM proposes to add an option called `auto_order` to Group that will tell the framework to compute the proper
subsystem order automatically using 
[Tarjan's strongly connected components algorithm](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm).
This algorithm groups the subsystems into strongly connected components (cycles) and topologically sorts those components.


## Example

```language=python
    p = om.Problem()
    model = p.model
    sub = model.add_subsystem('sub', om.Group())
    sub.add_subsystem('C5', om.ExecComp('y=5.0*x1 - 3.*x2'))
    sub.add_subsystem('C1', om.ExecComp('y=2.0*x'))
    sub.add_subsystem('C2', om.ExecComp('y=3.0*x1 + 4.*x2'))
    sub.add_subsystem('C4', om.ExecComp('y=5.0*x'))
    sub.add_subsystem('C3', om.ExecComp(['y=5.0*x', 'z=x']))
    sub.connect('C1.y', ['C2.x1', 'C5.x2'])
    sub.connect('C2.y', 'C4.x')
    sub.connect('C4.y', 'C3.x')
    sub.connect('C3.y', 'C2.x2')
    sub.connect('C3.z', 'C5.x1')
    sub.options['auto_order'] = True

    p.setup()
    p.run_model()

    # expected: [C1, C2, C4, C3, C5]
    # (C2, C3, and C4 form a cycle, so their initial order [C2, C4, C3] remains unchanged)
    print([s.name for s in sub._subsystems_myproc])
```


## Notes

1) Subsystems within a cycle will never be reordered, but if a cycle exists in a Group along with other
subsystems, then the cycle as a whole and the other subsystems will be ordered properly with respect to each other.

2) Auto ordering requires knowledge of all connections between systems in the model, so it must be done after all
connections are known.  Previous versions of OpenMDAO wouldn't have allowed this, because the order of their internal
data strucures, e.g., dicts containing variable metadata, were built up in subsystem execution order.
This meant that if the execution order were to change, then all of the internal data structures would have to be
rebuilt.  In order to prevent this, the subsystems of a Group are sorted alphabetically during setup of the 
internal data structures so that the order of variables in those data structures is decoupled from the subsystem
execution order.  This alphabetical sorting is done in all Groups, whether those Groups have set `auto_order` or 
not.  If for some reason a user does not want this sorting to occur, for example if they have a model that is
very sensitive to even slight numerical changes, they can set the `allow_post_setup_reorder` option
on the Problem to `False` to turn it off.  Turning it off will also disable all auto ordering.
