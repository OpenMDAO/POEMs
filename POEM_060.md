POEM ID: 060  
Title: Reports  
authors: robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

OpenMDAO is capable of outputting a variety of diagnostic information to both standard output and HTML files.

The current implementation isn't completely user friendly in two ways.

1. Prolific standard output can make it difficult to find relevant information when using diagnostics that print there, such as `p.list_problem_vars()`.
2. HTML reports often require the user consult the documentation to see how to enable a given report (assuming they know it exists), modify their code, and rerun.

This POEM proposes to turn on common reports **by default**.
This gives novice users this information for free.
All reports will be saved within a subfolder to avoid cluttering the current working directory and making cleanup easier.
Reports will be saved as HTML documents.

A good name for the subfolder might be `f'{sys.argv[0]}_{problem_name}_reports'` in the current working directory, so that multiple run files in the CWD don't overwrite reports made by each other.
Add `report_dir` as an option to Problem so that the user can override the default.

### Disabling report generation

Experienced users may not want to deal with generating reports on each run of their model, especially if their systems are especially large and the report generation is too time consuming.
This can be done by using a `reports` argument to Problem.setup (similar to checks), or by setting an environment variable `OPENMDAO_REPORTS`, where a value that is one of `['0', 'false', 'off']` (noisily) disables all report generation.

### How is this different than checks?

Checks will be diagnostic tests that issue warnings or raise exceptions.
Any current check that silently prints out information for review by the user and continues should be converted to saving an HTML report.

### Proposed Default Reports

- n2 (generated after setup)
- scaling_report (generated before run_driver)
- optimization_report (will be developed to support this POEM - replaces list_problem_vars, generated after run_driver)
- total_coloring (generated after run_driver)

### Extensibility

Developers of OpenMDAO-based libraries can add their own reports with `hooks._register_hook(func, class_name='Problem', pre=hook_func, post=hook_func)`.

Where `func` is a method of Problem (in this case) and `hook_func` is the function that generates the report, which either runs before or after `func` depending on whether it is given as `pre=` or `post=`.

It may makes sense to have a convenience method in problem (`register_report`) that associates a name with the report writing function.

### Potential API changes

If all non-warning, non-raising checks are converted to HTML reports, then available options to the `check` argument will change.
In addition, the logger function may be irrelevant after this change.
