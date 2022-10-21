POEM ID: 070  
Title: Inputs report  
authors: @robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2655](https://github.com/OpenMDAO/OpenMDAO/pull/2655)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

OpenMDAO makes it unnecessarily difficult to answer the question:

`What are the ultimate inputs to my problem, and what are their current values?`

When searching for the reason why a model isn't working as expected, the answer is often that an input isn't connected as it is expected to be.
Or that the user simply forgot to override the default value for a variable.

Given that we know:
1. All otherwise unconnected inputs should be coming from an IndepVarComp.
2. Any IVC output not overridden as a design variable by the optimizer is otherwise up to the user to specify.

We should be providing the user with a table of inputs, and by filtering the columns of the table by whether the variable is connected to an IVC, and
whether the variable is connected to a design variable, it should be easy for the user to see all of the "user-settable" inputs in their model, and their current values.

## Secondary and prerequisite tasks

- Replacing tabulate with a `generate_table(dict, out_file, format='stdout|markdown|html)` function.

OpenMDAO currently relies on the tabulate package to generate tables, but this is a fairly lightweight dependency that we can drop.
Option stdout will be used to replace those functions which currently use tabulate to write output to stdout.

- Make all reports have a common look and feel

Once our own HTML tables are generated, we can unify the look and feel of some of the reports (connections viewer, optimization report, this inputs report) by applying a common theme from the `tabulator.js` library to them.

The connections viewer already uses tabulator.js, so its really just a matter of applying the same CSS to the other reports.

## Columns for the inputs report

The inputs report should have the following columns which will be sortable and filterable:
- absolute name
- promoted name
- source name
- source is ivc (checkbox)
- source is desvar (checkbox)
- units
- shape
- tags
- val
- min val
- max val

## Determining "ultimate inputs"

Once the report is generated, the user can see the inputs for which they are responsible by filtering the data to show only the `source is ivc (True)` and `source is desvar (False)` columns.
