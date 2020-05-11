POEM ID: 011
Title: Expand problem recording options
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
There are currently many examples of inconsistency and limitations in the API and documentation of case recording. 

* The user is limited in what can be recorded from a Problem. For example, derivatives cannot be recorded. 
  This is useful for saving data at a single case without using a ton of memory to store data at every iteration 
  of the driver or solver. There's a particular hangup with derivatives, since `compute_totals` can be called with 
  somewhat different behavior by either the Driver or the Problem.
* The API is in some cases inconsistent and misleading:
    * Recording of System "metadata" is really recording of System options. The API should reflect that.
    * Problem.record_iteration is not the recording of an iteration, but the state at a moment in time
    * There is a recording option called record_derivatives but the attribute that is used to retrieve that 
    data is called jacobian
* To have a complete picture of the model in all case recorder files, metadata and options for the model and all 
  systems should always be recorded
* The documentation does not make clear what is being recorded with all the recording options and how to access the 
  values being recorded.
* abs2prom is always being recorded. It is also recorded into another table when the init arg, model_viewer_data,
  to CaseRecorder is True
* Responses just means objectives and constraints so no need for a separate recording_option for responses



Description
===========

This POEM suggest the following rules of thumb for recorders:

* Systems should support recording inputs, outputs, residuals, metadata, model_metadata
* Drivers should support options for their associated system, as well as the driver-specific options for recording 
  objectives, constraints, desvars, responses, and derivatives.
* Solvers should support options for their associated system, as well as the solver-specific options for recording 
  abs_err, rel_err, and solver residuals
* Problem recorders should support the recording options of the underlying systems, drivers, and **all** underlying 
  solvers.  If the problem recorder is given the options to _record_solver_residuals_, we should record those for all 
  the solvers in the model when `problem.record_iteration()` is called

To address the limitations on what gets recorded automatically and optionally, this table below 
summarizes the recording options changes for each of the four OpenMDAO entities which can be recorded.

| Record Options          | Driver | System | Solver | Problem |
|-------------------------|--------|--------|--------|---------|
| record_constraints      |   x    |        |        |    x    |
| record_desvars          |   x    |        |        |    x    |
| record_objectives       |   x    |        |        |    x    |
| record_derivatives      |   x    |        |        |    o F  |
| record_responses        |   x    |        |        |    x    |
| record_inputs           |   x    |    x   |    x   |    o F  |
| record_outputs          |   o T  |    x   |    x   |    o T  |
| record_residuals        |   o F  |    x T |    o F |    o F  |
| record_metadata         |   x>a  |    x>a |    a   |    a    |
| record_model_metadata   |   x>a  |    x>a |    a   |    a    |
| record_abs_error        |        |        |    x T |    o F  |
| record_rel_error        |        |        |    x T |    o F  |
| record_solver_residuals |        |        |    x F |    o F  |
| includes                |   x    |    x   |    x   |    x    |
| excludes                |   x    |    x   |    x   |    x    |
| options_excludes        |   o    |    x   |    o   |    o    |

x - Existing option
o - Proposed new option
a - Always record
x>a - was optional now always
T or F - default for that option


This POEM also covers other modifications to the API, internals, and documentation for case recording:

* Currently, to record a Problem, the method is `record_iteration`. An iteration is not being recorded. A snapshot 
  in time of the Problem is being recorded. The method name will be changed to `record_state`.
* Recording of metadata and model metadata will always happen. The recording options 
  `record_metadata` and `record_model_metadata` will be deprecated.
* Access to the derivatives is currently through the `jacobian` attribute on a `Case`. To maintain consistency with 
  the option `record_derivatives`, the attribute `jacobian` will be deprecated and replaced with `derivatives`.
* Some of the "metadata" being recorded is actually considered "options" now in OpenMDAO. 
  Change the way users access that information to reflect that. This will also bring consistency to the API since there
  is a recording_option called `options_excludes` that applies to what is currently called recording_metadata. Deprecate
  using SqliteCaseReader.system_metadata and replace with SqliteCaseReader.system_options
* Document the kinds of metadata, options, and record_viewer_data that get recorded in the cases.
* Document better how to access the data that is being recorded
* Do not record abs2prom when recording model_viewer_data. It is already available from the metadata table.
* Deprecate the record_responses recording_option
* Work on adding the new options from the table above:
    * Add recording of derivatives to Problem !
    * Add recording of inputs, outputs, and residuals to Problem !
    * Add recording of outputs and residuals to Driver !
    * Add recording of (System) residuals to Solver ????? Do we need this ?
    * Add recording of metadata aka options for all Systems to Solver and Problem !
    * Add recording of record_abs_error, record_rel_error, and record_solver_residuals to Problem
    * Add options_excludes to Driver, Solver, and Problem !
* Update the docs to be more clear about what recording option to set for a given need and then how to get that data
    * If I want to record X
    * What recording option do I set?
    * How do I get to it after the recording is done
    
To break this large POEM into manageable PRs, it is proposed to do these PRs:

* PR #1
    * Always record metadata and options for all recording of System and Driver. 
        Deprecate `record_metadata` and `record_model_metadata`
    * Change the Case.jacobian attribute to Case.derivatives
    * Change `Problem.record_iteration` to `Problem.record_state`
* PR #2
    * Deprecate using SqliteCaseReader.system_metadata and replace with SqliteCaseReader.system_options
* PR #3
    * Do not record abs2prom when recording model_viewer_data. It is already available from the metadata table.
* PR #4
    * Add recording of metadata aka options for all Systems to Solver and Problem
    * Add options_excludes to Driver, Solver, and Problem
* PR #5
    * Add recording of derivatives to Problem
* PR #6
    * Add recording of inputs, outputs, and residuals to Problem. Add recording of outputs and residuals to Driver
* PR #7
    * Add recording of record_abs_error, record_rel_error, and record_solver_residuals to Problem
 
 
 Update the format_version value in the case recording file as needed.


References
----------

N/A
