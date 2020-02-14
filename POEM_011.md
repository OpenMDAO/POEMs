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
| record_outputs          |   o    |    x   |    x   |    o    |
| record_residuals        |   o    |    x   |    o   |    o    |
| record_metadata         |   o    |    x   |    x   |    o    |
| record_model_metadata   |   x    |    x   |    o   |    o    |
| record_abs_error        |        |        |    x   |    o    |
| record_rel_error        |        |        |    x   |    o    |
| record_solver_residuals |        |        |    x   |    o    |
| options_excludes        |        |    x   |        |    o    |

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

This POEM suggest the following rules of thumb for recorders:

* Systems should support recording inputs, outputs, residuals, metadata, model_metadata
* Drivers should support options for their associated system, as well as the driver-specific options for recording objectives, constraints, desvars, responses, and derivatives.
* Solvers should support options for their associated system, as well as the solver-specific options for recording abs_err, rel_err, and solver residuals
* Problem recorders should support the recording options of the underlying systems, drivers, and **all** underlying solvers.  If the problem recorder is given the options to _record_solver_residuals_, we should record those for all the solvers in the model when `problem.record_iteration()` is called

In addition, we should make the `record_metadata` and `record_model_metadata` options more clear.  What's the distinction between them.  Since we've replaced `metadata` with `options` we should probably change these to reflect that.

References
----------

N/A
