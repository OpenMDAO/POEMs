POEM ID: 013
Title: Unit conversion enhancements
Authors: @robfalck
Competing POEMs: [N/A]  
Related POEMs: [N/A]
Associated implementation PR: N/A

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

Motivation
==========

OpenMDAO's unit conversion is powerful but it should be easier for
users to take advantage of our unit conversion tools in their models.
Sometimes unit conversion within the compute/compute_partials methods
is necessary, and we should provide a way of doing so consistently with
the same conversion factors used internally within OpenMDAO.

Description
===========

This enhancement involves two changes:
1. `openmdao.utils.units.convert_units` will be added to `openmdao.api`
2. `openmdao.utils.units.get_conversion(from, to)` will be added to `openmdao.api` and renamed to `unit_conversion(from, to)`.  The existing `get_conversion` will be deprecated.

References
----------

N/A
