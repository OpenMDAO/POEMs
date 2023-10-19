POEM ID: 082  
Title: Add ability to easily retrieve all independent variables within a Problem.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2871](https://github.com/OpenMDAO/OpenMDAO/pull/2871)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

User's sometimes struggle with knowing what the actual "inputs" for a model are.
The `list_inputs` method list all inputs within a model, component by component, but many of these are connected to
other outputs already.
What the user utimately needs to know is "What are the inputs that this Problem expects me to provide?"
As problem size and complexity increases, it has become necessary for OpenMDAO to make it easier for a user to 
know what a Problems inputs are.

## Proposed Solution

All OpenMDAO inputs have been connected to an output since the advent of Automatic IndepVarComp (autoIVC).
Anything that the user is expected to provide a model is an IndepVarComp output (or in a component that they've
created that has IndepVarComp-like behavior).
This POEM proposes to add a method to Problem that retrieves a mapping of the promoted independent variable names in the model,
along with their associated metadata.


This method will be called `list_indep_vars`.


To find all of the independent variables in a model that the user needs to be aware of we will check all connections
in the model and find those connected to an output that is tagged with `'openmdao:is_indep_var'`.  This covers
IndepVarComp outputs, as well as custom user components with IndepVarComp-like behavior.
We then create a set of the promoted name of those inputs, and return them along with a mapping to the metadata
of the associated independent variable output.

Optionally, we will provide the ability to omit independent variables that are also design variables.

