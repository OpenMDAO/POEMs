POEM ID: 017    
Title: User can specify units when adding design variables, constraints, and objectives.  
authors: @Kenneth-T-Moore         
Competing POEMs: [N/A]   
Related POEMs: [N/A]  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1265  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------


Description
-----------

The `add_design_var`, `add_constraint`, and `add_objective` signatures will be modified to take a units
argument, e.g.

```
        prob.model.add_design_var('indeps.x', lower=-50, upper=50, units='ft')
```

OpenMDAO will check compatibility, and raise an exception if the target is incompatible or has no units.  All
other arguments are considered to be specified in the units defined in "units".  Internally, the unit
conversion will be added to existing driver scaling, with unit conversion factor applied first, then the
scaler/adder or ref/ref0.



