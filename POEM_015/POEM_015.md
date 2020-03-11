POEM ID: 015 
Title: Automatic creation of IndepVarComp outputs for all unconnected inputs
authors: [justingray]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: 

Status:
  
- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
==========

ndepVarComp outputs have always been a weird aspect of OpenMDAO models.
For one thing, users often think of them as "model inputs" but they are created with an `add_output` method. 
Though most users quickly learn how to use them, they are still somewhat annoying to have to add to models, especially in certain specific situations: 

    - If you have a group that is meant to both stand-alone and be 
    used as a subsytem in a larger model, then you sometimes have to add some if statements to control whether or not IndepVarComps should be created in your group 
    - If you are using a group that already has IndepVarComp outputs inside it, and you want to pass variables into that group instead you then need to modify the group itself so you can issue the connections 

From a user perspective, the need is to allow any particular variables (that is otherwise unconnected to anything) to either behave as its own source or design variable (i.e. its own IndepVarComp output) or to be connected into by some other source.
However, due to internal details of OpenMDAO and the MAUD equations it uses you can't actually implement things that way.
Only IndepVarComp outputs can be design variables, but no outputs can be the target side of a connection. 

Util the integration of POEM_003 --- allowing the addition of I/O during configure --- there was no way around this problem. 
Post 003, there is now a solution. 
As the very last step in the setup-stack (after all user setup and configure operations have been called), the framework can find all of the unconnected inputs, create an associated IndepVarComp output and connect it to that hanging input.




Description
===========
The goal of this POEM is to be 99.5% backwards compatible with all older models. 
If you like your IndepVarComps, you can keep them. 
If you don't want to have OpenMDAO do this automatic-ivc creation, you can turn it off via `problem.setup(auto_ivc=False)`. 

However, it is expected that most users will perfer to leave the automatic-ivc functionality running and hence this POEM proposes that `auto_ivc=True` will be the default state for the new feature. 

Where the `auto_ivc` will live
------------------------------
All automatically created IVC outputs will live in the `auto_ivc` component which will automatically get added to the top level of any model. 
This component will always be present in all models, and will be visible in the n2 diagram. 
The framework will create explicit connections between any `auto_ivc` output and its assocaited inputs. 

`auto_ivc` output naming
-------------------------
To keep thing simple, and because in any normal usage the user will never have to directly address any auto_ivc outputs by their own name, the outputs of the `auto_ivc` component will be named as : ['v0', 'v1', 'v2', ... 'v<n>'] where `n` is 1 less than the number of unconnected input variables in the model before `setup()` was called

`problem.model` must always be a group
--------------------------------------
As of V3.0, it was allowable for the top level of a model to be either an instance of `Component` or of `Group` (i.e. any instance of `System`). 

Now, the framework will be automatically adding an `auto_ivc` component to the top level of model, that top level must always be a group. 


Changes to the way you set/get variables
----------------------------------------
As of V3.0 users address all outputs using their `promoted name` and all inputs using the `absolute name`.
Both the `promoted_name` and the `absolute_name` are unique (one pointed to the unique source, the other to the unique input). 
90% of the time, you just set values to the promoted names for things. 
The exception happens when you have unconnected inputs. 
If you have a single unconnected input, then you set that value using the absolute path name for that input. 
However, if you have promoted multiple inputs in a group to the same name and left that promoted path unconnected, then you have a weird situation. 
To set the value for that promoted-but-unconnected input you must manually set the value to the absolute path of all the individual inputs that are promoted to the same name. 
To work around this, users will normally create an IndepVarComp in the same group as the promoted-but-unconnected input, add an output to it and  promote that output to the same name as the input. 
Then you could set/get using the promoted name.  

This POEM will change this paradigm. 
Since there will be no unconnected inputs any more, every single variable will have an associated output and hence will have an associated source.
There will no longer be unique names for outputs or inputs, but rather every variable at every level of the hierarhcy has a `natural_name`, which can always be resolved to its source. 
Users will set/get variables with any valid `natural_name`, 
and OpenMDAO will resolve that to the source name before performing the set/get operation on true source. 

Stated another way, re-iterate, users will no longer be able to set input values for anything directly. 
Instead, all variable names will be resolved to their `source_name` before set/get operations. 

**Example:**
![example model to understand `natural name` vs `source name`](/POEM_015/poem_015_example_model.jpg)]

In this example, you have two components (`C0`, `C1`), down inside two nested groups (`G0`, and `G1`). 
Both `C0` and `C1` have an input `X` which has been promoted up to the level of `G0`. 
Both component `C0` and `C1` have an output `Y`, but only `C1` has promoted that output to the level of `G0`. 

The following are all valid `natural_names` and matched up `source_names` for this model.

| natural name  |  source name  |
---------------------------------
| auto_ivc.V0   | auto_ivc.V0   |
| G0.X          | auto_ivc.V0   |
| G0.C0.X       | auto_ivc.V0   |
| G0.C1.X       | auto_ivc.V0   |
| G0.C0.Y       | G0.C0.Y       |
| G0.C1.Y       | G0.C1.Y       |
| G0.Y          | G0.C1.Y       |






Setting defaults for promoted inputs in groups 
-----------------------------------------------


Backwards Incompatible API Changes
----------------------------------

    - Problem.model can no longer be a single component
    - Previously, if you had a model with an unconnected promoted input at the group level, you could manually set the  values of each of the component inputs to a different value by addressing each one by its absolute name (i.e. its full path name). 
    Now, when you set the value of any input by its full-path-name, you will also be setting the value of all other inputs to same value (or the equivalent value converted to the local units of the other inputs). 
    (there is not good reason that I can think of you would do this... but if you are, then you will see different behavior)







API Descri

