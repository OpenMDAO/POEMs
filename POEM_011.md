POEM ID: 011
Title: Expand problem recording options
Authors: @robfalck
Competing POEMs: [N/A]  
Related POEMs: [N/A]
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
==========
Currently OpenMDAO supports `Problem.record_iteration()` to record the current state of the Problem.
This is useful for saving data at a single case without using a ton of memory to store data at every iteration of the driver or solver.
However, Problem recording currently only supports a limited subset of recording options:  the user cannot
record inputs if they only want a single iteration recorded.

The table below summarizes the record options for each of the four
things which can be recorded.

| Record Options          | Driver | System | Solver | Problem |
|-------------------------|--------|--------|--------|---------|
| includes                |   x    |    x   |    x   |    x    |
| excludes                |   x    |    x   |    x   |    x    |
| record_constraints      |   x    |        |        |    x    |
| record_desvars          |   x    |        |        |    x    |
| record_objectives       |   x    |        |        |    x    |
| record_derivatives      |   x    |        |        |    o    |
| record_responses        |   x    |        |        |    x    |
| record_inputs           |   x    |    x   |    x   |    o    |
| record_outputs          |        |    x   |    x   |    o    |
| record_residuals        |        |    x   |        |    o    |
| record_metadata         |        |    x   |    x   |         |
| record_model_metadata   |   x    |    x   |        |    o    |
| record_abs_error        |        |        |    x   |         |
| record_rel_error        |        |        |    x   |         |
| record_solver_residuals |        |        |    x   |         |
| options_excludes        |        |    x   |        |         |

x - Existing option
o - Proposed new option

Description
===========

In order to make it possible to record more about the problem with a single iteration,  
this POEM proposes that the following recording options be allowed for Problem:

* record_derivatives
* record_inputs
* record_outputs
* record_residuals
* record_model_metadata

There's a particular hangup with derivatives, since `compute_totals` can be called with somewhat different behavior
by either the Driver or the Problem.  This option would require that Problem.compute_totals be called if set to True.

References
----------

N/A
