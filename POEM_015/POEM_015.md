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

IndepVarComp outputs have always been a weird aspect of OpenMDAO models.
For one thing, users often think of them as "model inputs" but they are created with an `add_output` method. 
Though most users quickly learn how to use them, they are still somewhat annoying to have to add to models, especially in certain specific situations: 

    - If you have a group that is meant to both stand-alone and be 
    used as a subsytem in a larger model, then you sometimes have 
    to add some if statements to control whether or not IndepVarComps 
    should be created in your group 

    - If you are using a group that already has IndepVarComp outputs inside it, 
    and you want to pass variables into that group instead you then need to 
    modify the group itself so you can issue the connections 

From a user perspective, the need is to allow any particular variables (that is otherwise unconnected to anything) to either behave as its own source or design variable (i.e. its own IndepVarComp output) or to be connected into by some other source.
However, due to internal details of OpenMDAO and the MAUD equations it uses you can't actually implement things that way.
In OpenMDAO V3.0 once an input is connected to an IndepVarComp output (i.e. you wanted to use it as a design variable), you can no longer connect anything else into that input variable. 

Until the integration of POEM_003 --- allowing the addition of I/O during configure --- there was no way around this problem. 
Post 003, there is now a solution. 
As the very last step in the setup-stack (after all user setup and configure operations have been called), the framework can find all of the unconnected inputs, create an associated IndepVarComp output and connect it to that hanging input.


Description
===========
If you like your manually created IndepVarComps, you can keep them. 
However, the goal of this POEM is to make them largley obsolete.

To maintain backwards compatibility, users can pass `auto_ivc=True` or `auto_ivc=False` as arguments to setup. 
When `auto_ivc=False` OpenMDAO will effectively behave the same way it does now, though it will still opperate under the new variable naming paradigm.

Variable Naming Paradigm
------------------------
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

Stated another way, with `auto_ivc=True`, users will no longer be able to set input values for anything directly. 
Instead, all variable names will be resolved to their `source_name` (which will be an output) before set/get operations. 

**Example:**
![example model to understand `natural name` vs `source name`](/POEM_015/poem_015_example_model.jpg)]

In this example, you have two components (`C0`, `C1`), down inside two nested groups (`G0`, and `G1`). 
Both `C0` and `C1` have an input `X` which has been promoted up to the level of `G0`. 
Both component `C0` and `C1` have an output `Y`, but only `C1` has promoted that output to the level of `G0`. 

The following are all valid `natural_names` and matched up `source_names` for this model.

| `natural_name`| `source_name` |
|---------------|---------------|
| auto_ivc.V0   | auto_ivc.V0   |
| G0.X          | auto_ivc.V0   |
| G0.C0.X       | auto_ivc.V0   |
| G0.C1.X       | auto_ivc.V0   |
| G0.C0.Y       | G0.C0.Y       |
| G0.C1.Y       | G0.C1.Y       |
| G0.Y          | G0.C1.Y       |


Where the `auto_ivc` component will live
----------------------------------------
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

Resolving which unit should be applied
--------------------------------------

Though there are potentially many valid `natural_names` all pointing to the same source name, 
it is not required that all the inputs have the same units defined. 
When using the `Problem.__getitem__` and `Problem.__setitem__` (e.g. `prob['some_var'] = 3`) the unit will be matched to the specific unit defined with that `natural_name`.

Consider the example from above. 
If `G0.C0.X` was defined in centimeters, and `G0.C1.X` was defined in meters then 
`prob['G0.C0.X'] = 3` will mean something different than `prob['G0.C1.X'] = 3`. 

To combat this, users can be more explicit via the `Problem.get_val` and `Problem.set_val` which allow for a `units=<something>` argument to be given so the intent is clear. 


Setting defaults for promoted inputs in groups 
-----------------------------------------------

In cases where the auto-ivc output connects to a single input, the value and unit of that output can be taken directly from the input. 
When there is are two or more inputs promoted to a group level, the default value and unit can become ambiguous if any of the values/units differ amongst the promoted set. In the case of any amiguity, users can call `group.add_input(...)` and provide the necessary default information. 

An auto-ivc output will be created and connected to any group level variable declared by `add_input` *if and only if* there is no source connected to that input when `probem.setup()` is called. 

Notes:

    - `add_input` at the group level will take the same arguments as `add_input` at the component level 
    - the unit information given in `add_input` will define the units used when setting/getting values using that `natural_name`
    - there is no `add_output` at the group level!

Backwards Incompatible API Changes
----------------------------------

    - Problem.model can no longer be a single component
    - Previously, if you had a model with an unconnected promoted input at the group level, you could manually set the  values of each of the component inputs to a different value by addressing each one by its absolute name (i.e. its full path name). 
    Now, when you set the value of any input by its full-path-name, you will also be setting the value of all other inputs to same value (or the equivalent value converted to the local units of the other inputs). 
    (there doesn't seem to be any obvious reason why a user would have set inputs in this way,  but if you are doing that then you will see different behavior)


Implementations Risks
---------------------

    - This POEM will cause a modest increase in the amount of memory allocated, because there will be new space added to the output vector for the automatically created IVC outputs. 
    - There will be an additional data-transfer involved with the new automatically created IVC output, which will cause some additional overhead. 

    The magnitude of these effects will depend on how many unconnected inputs you have, but we anticipate the overall impact to be relatively small. 
    It is possible that some internal refactoring on the data-vectors may be able to mitigate the increased memory needs, but the additional data transfer will still be there. 
    Before acceptance, some performance benchmarking will need to be performed to ensure performance remains high. 


