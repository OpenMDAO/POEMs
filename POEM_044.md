POEM ID: 044  
Title: OpenMDAO-Specific Warnings  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

OpenMDAO currently uses Python's UserWarning as the basis for most warnings.
Some warnings can be annoyingly verbose, but filtering out all UserWarnings is likely overkill.
This POEM proposes providing OpenMDAO-specific warnings and some API functions to allow the user to silence unwanted warnings.


Proposed Warning Classes
------------------------

There are two goals with creating OpenMDAO-specific warning classes.

1. Make it possible to silence or otherwise alter the behavior of some warnings.
2. Don't make an unwieldy number of warning classes.

Using a hierarchical approach, this proposes the following:

The top of the OpenMDAO warning hierarchy will be class `OpenMDAOWarning`, derived from the UserWarning class.
The following classes will derive from `OpenMDAOWarning`.

| Warning Class           | String Name         | Default Behavior     | Description                                                         |
| ----------------------- | ------------------- | -------------------- | ------------------------------------------------------------------- |
| SetupWarning            | warn_setup          | always               | Parent-class of all setup-time warnings (not errors).               |
| SolverWarning           | warn_solver         | always               | Warning encountered during solver execution.                        |
| DriverWarning           | warn_driver         | always               | Warning encountered during driver execution.                        |
| UnusedOptionWarning     | warn_unused_option  | always               | A given option or argument has no effect.                           |
| CaseRecorderWarning     | warn_case_recorder  | always               | Warning encountered by a case recorder or case reader.              |
| CacheWarning            | warn_cache          | always               | A cache is invalid and must be discarded.                           |

For fine-grain control of setup warnings, the following classes will derive from `SetupWarning`.

| Warning Class               | String Name         | Default Behavior     | Description                                                            |
| --------------------------- | ------------------- | -------------------- | ---------------------------------------------------------------------- |
| PromotionWarning            | warn_promotion      | always               | Behavior regarding ambiguities due to promotion or set_input_defaults. |
| UnitsWarning                | warn_units          | always               | Warning pertaining to units (usually unitless to dimensional).         |
| DerivativesWarning          | warn_derivatives    | always               | Warning regarding derivatives (usually approximation or coloring).     |
| MPIWarning                  | warn_mpi            | always               | Warning regarding MPI availability.                                    |
| DistributedComponentWarning | warn_distributed    | always               | Warning regarding distributed component setup.                         |


Another non-user-facing warning will also be created, derived from UserWarning:  `AllowableSetupError`.  This class
will default to a behavior of "error" and will allow some setup errors to pass in order for the N2 to be built.  This  way,
even if `OpenMDAOWarning` is set to `'ignore'`, setup errors will continue to be triggered unless setup is being performed
only for the purpose of creating an N2 diagram via the command line interface.


Setting Warning Verbosity
-------------------------

OpenMDAO-specific warnings may take effect prior to setup.
For example, some warnings are triggered when adding inputs.
For this reason, the warning behavior needs to be triggered by a function call before the first warning is issued

The verbosity of all OpenMDAO warnings will be set when OpenMDAO is initially imported.

Users will be free to use Python's warnings filter system:

```
import warnings
import openmdao.api as om
warnings.filterwarnings(action='ignore', category=om.UnitsWarning)
```

In addition, an OpenMDAO API function will also be available.
This function will be similar to numpy's seterr method.

```
import openmdao.api as om
om.filter_warnings(warn_units='ignore')
```

Issuing Warnings
----------------

To issue warnings in a standard format, the OpenMDAO API will have a
new `issue_warning` method that functions similarly to the existing simple_warning function.
This will take the same "stringified" name that the filter_warnings function takes, along
with a prefix to be used that will typically identify the path of the system issuing the warning.

```
import openmdao.api as om

om.issue_warning(warn_mpi='Unable to perform action, MPI is not available.', prefix=self.pathname)
```

Valid Actions for Filtering
---------------------------

OpenMDAO will use the same actions that are available in Python, with one addition.
To conform to a numpy-like interface, an action of `'raise'` will have the same effect as `'error'`.

The following table is from the Python warning documentation:

| Value       | Disposition                                                                                                             |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| "default"   | print the first occurrence of matching warnings for each location (module + line number) where the warning is issued    |
| "error"     | turn matching warnings into exceptions  (OpenMDAO will also accept "raise")                                             |
| "ignore"    | never print matching warnings                                                                                           |
| "always"    | always print matching warnings                                                                                          |
| "module"    | print the first occurrence of matching warnings for each module where the warning is issued (regardless of line number) |
| "once"      | print only the first occurrence of matching warnings, regardless of location                                            |


Registering Warnings
--------------------

Developers of libraries built on top of OpenMDAO may want to add their own warnings to the ecosystem.
To do this, they should define their warning class and provide it with two class properties: a name and a default filter.

```
class MySetupWarningClass(om.SetupWarning):
    name = 'warn_my_setup'
    filter = 'always'
```

Then, to register it with OpenMDAO:

```
om.register_warning(MySetupWarning)
```

The `register_warning` function will apply the filter and add the warning class to an internal dictionary so that it can be accessed using its string name.
