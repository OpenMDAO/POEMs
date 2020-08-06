POEM ID: 020  
Title: KSComp option to automatically add corresponding constraint  
Authors: @robfalck
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1323  

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated

OpenMDAO developers are accepting this without discussion.

Motivation
==========

KSComp is generally used to add a quantity for constraint, similar to
EQConstraintComp.  This modification proposes adding a new option
`add_constraint` to automatically add this constraint during setup.


Description
===========

The following new options are added to KSComp to allow it to add
a constraint automatically during setup:

`add_constraint` - If True, add a constraint to the problem
`scaler` - Constraint scaler
`adder` - Constraint adder
`ref0` - Constraint zero reference
`ref` - Constraint unit reference
`parallel_deriv_color` - Constraint parallel deriv color

References
----------

N/A
