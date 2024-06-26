POEM ID: 097  
Title: Output file reorganization.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR:  

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

OpenMDAO currently outputs a number of files to various locations.

- ./reports/problem_name/{report_name}.html
- ./coloring_files/
- ./{recorder_file}.sql
- ./IPOPT.out (and others for various optimizers)

Aside from reports, these files aren't associated with a particular problem which can make organization difficult. Furthermore, the notion of cleaning up stale outputs is challenging due to the flat file structure and a lack of understanding which files pertain to which outputs.

## Proposed Solution

- OpenMDAO problems will have a single output directory under which all outputs are placed.

- A problem's `get_outputs_dir()` method will provide a pathlib.Path object of the output directory, and create it if necessary.

- The output directory name will be `f'{problem._name}_out'`

- Problems will have the notion of a parent, which can be another problem or a System (associated with another Problem). This will be useful for subproblems. If it has a parent, a problem's output files will nest under its output directory. Notionally it would look something like this:

```
./outer_problem_out
    coloring_files
    driver_rec.db
    openmdao_checks.out
    IPOPT.out
    reports/
       n2.html
    sub_problem_out/
       coloring_files/
       openmdao_checks.out
       reports/
        n2.html
       solver_rec.db
```

## Notable changes in the API

- **The reports directory cannot be changed** (either through set_reports_dir or through the OPENMDAO_REPORTS_DIR environment variable).

- **Reports can no longer be executed pre-setup.** The hierarchy of problems is not known until setup so the reports directory will not exist until the problem has begun its setup.

- The `coloring_dir` will be used for loading in existing colorings, but problems should save the used colorings to `f'{output_dir}/coloring_files'`.

- Recording files should be specified as filename only, and will be placed in the `f'{outputs_dir}'`