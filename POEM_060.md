POEM ID: 060  
Title: Reports  
authors: robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: N/A

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

OpenMDAO is capable of outputting a variety of diagnostic information to both standard output and HTML files.

The current implementation isn't completely user friendly in two ways.

1. Prolific standard output can make it difficult to find relevant information when using diagnostics that print there, such as `p.list_problem_vars()`.
2. HTML reports often require the user consult the documentation to see how to enable a given report (assuming they know it exists), modify their code, and rerun.

This POEM proposes to turn on common reports **by default**.
This gives novice users this information for free.
All reports will be saved within a subfolder to avoid cluttering the current working directory and making cleanup easier.
Reports can be various formats that allow for more rich content than flat text, such as HTML files.

### Where the reports go

1. Reports will be saved in the current working directory in under a directory named `reports` by default.
2. The environment variable `OPENMDAO_REPORTS_DIR` can be set to override this default.
3. `Problem` will have a new argument `reports_dir` which will be `_UNDEFINED` by default and used to override the environment variable if necessary.  This will allow users to run multiple scripts/notebooks from the same directory without any issues in collisions with the reports.
4. Each problem encountered will create a directory _within_ the `reports_dir` that will contain reports for that problem.  Thusn, unless explicitly disabled, subproblems will generate their own reports.

### Disabling report generation

Experienced users may not want to deal with generating reports on each run of their model, especially if their systems are especially large and the report generation is too time consuming.  This can be accomplished in the following ways.

1. The environment variable `OPENMDAO_REPORTS`, where a value that is one of `['0', 'false', 'off', 'none']` (noisily) disables all report generation.
2. The `Problem` argument `reports`.  By default it will be `_UNDEFINED`, but otherwise mirrors the `OPENMDAO_REPORTS` environment variable.  A value of `False` or `None` or an empty list disables report generation.  A "truthy" value enables all reports, and a list of strings only enables those reports listed.

### How is this different than checks?

Checks will be diagnostic tests that issue warnings or raise exceptions.
Any current check that silently prints out information for review by the user and continues should be converted to saving an HTML report.

### Proposed Default Reports

- n2 (generated after setup)
- scaling_report (generated before run_driver)
- total_coloring (generated after run_driver)

### Extensibility

The reports system uses OpenMDAO's notion of hooks to generate reports at various stages (pre/post setup, driver execution, etc).
User's may register new reports using the `register_reports` method.

```
def register_report(name, func, desc, class_name, method, pre_or_post, inst_id=None):
    """
    Register a report with the reporting system.
    Parameters
    ----------
    name : str
        Name of report. Report names must be unique across all reports.
    func : function
        A function to do the reporting. Expects the first argument to be an instance of class_name.
    desc : str
        A description of the report.
    class_name : str
        The name of the class owning the method where the report will be run.
    method : str
        In which method of class_name should this be run.
    pre_or_post : str
        Valid values are 'pre' and 'post'. Indicates when to run the report in the method.
    inst_id : str or None
        Either the instance ID of an OpenMDAO object (e.g. Problem, Driver) or None.
        If None, then this report will be run for all objects of type class_name.
    """
```

### API changes

The following API changes will be made as part of this POEM

1. The ability to disable recording when invoking `run_solve_nonlinear`, `run_model`, and `run_driver` with a `record` argument which defaults to True.

In the process of implementation we have found that some reports, which need to execute the model, will cause a recording iteration which may not be wanted by the user.  This argument will give us the ability to avoid unwanted recording iterations when reports are being generated.

If all non-warning, non-raising checks are converted to HTML reports, then available options to the `check` argument will change.
In addition, the logger function may be irrelevant after this change.
