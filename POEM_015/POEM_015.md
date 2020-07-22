POEM ID: 015 
Title: Automatic creation of IndepVarComp outputs for all unconnected inputs
authors: [justingray]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: 

Status:
  
- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
==========

IndepVarComp outputs have always been a weird aspect of OpenMDAO models.
For one thing, users often think of them as "model inputs" but they are created with an `add_output` method. 
Though most users quickly learn how to use them, they are still somewhat annoying to have to add to 
models, especially in certain specific situations: 

* If you have a group that is meant to both stand-alone and be 
used as a subsystem in a larger model, then you sometimes have 
to add some if statements to control whether or not IndepVarComps 
should be created in your group 

* If you are using a group that already has IndepVarComp outputs inside it, 
and you want to pass variables into that group instead you then need to 
modify the group itself so you can issue the connections 

**Example:**
Consider a group `G0`, with a promoted input `X` that maps to the inputs on two subsystems `C0` and `C1`. 
If you wanted to use `G0` at the top level of your mdoel and optimize the value of `X`, then you 
would get a model that looked like this: 
![example model to illustrate an IVC for a DV](/POEM_015/poem_015_problem_ivc.jpg)]

However, if you wanted to connect some other calculation into `G0.X`, from the outside of `G0` then 
you would get a model like this: 
![example model to illustrate an external connection for the same input](/POEM_015/poem_015_problem_connection.jpg)]

So now you need code that goes something like this: 

```
import openmdao.api as om

class AGroup(om.Group): 

    def intialize(self): 
        self.options.declare('owns_dvs', default=True)
    
    def setup(self): 
        if self.options['owns_dvs']: 
            dvs = self.add_subsystem('dvs', IndepVarComp(), promotes=['*'])
            dvs.add_output('X', value=10, units='furlongs/fortnight')

        **do other stuff**
        . 
        . 
        . 

if __name__ == "__main__": 

    # To use G0 stand alond
    p = om.Problem()
    p.model.add_subsystem('G0', AGroup(owns_dvs=True))
    p.model.add_design_var('G0.X', lower=-1, upper=1)

    # To use G0 with some other component
    p = om.Problem()
    
    dvs = p.model.add_subsystem('dvs', IndepVarComp(), promotes=['*'])
    dvs.add_output('speed', -4, units='furlongs/fortnight')
    p.model.connect('speed', 'some_comp.speed')
    p.model.add_subsystem('some_comp', 
                          om.ExecComp('X=speed+3', units='furlongs/fortnight'))
    p.model.add_subsystem('G0', AGroup(owns_dvs=False))
    p.model.connect('some_comp.X', 'G0.X')

    p.model.add_design_var('speed', lower=-4, upper=-2)
```

The addition of the option variable adds a few lines of code, but that is just for one variable. 
If you had 4 different variables that you wanted to control the ownership of in a granular fashion, 
then you would need four different options. 
Also, a user might not realize that they needed to set `owns_dvs=False` when using this group in a 
larger model, and hence would get a connection error when they tried to use it. 

Until the integration of POEM_003 --- allowing the addition of I/O during configure --- there was 
no way around this problem. Post 003, there is now a potential solution. 
As the very last step in the setup-stack (after all user setup and configure operations have been called), 
OpenMDAO can find all of the unconnected inputs, create an associated IndepVarComp output and 
connect it to that hanging input.

Then the code could look like this instead: 

```
import openmdao.api as om

class AGroup(om.Group): 
    
    def setup(self): 

        self.set_input_defaults('X', units='furlongs/fortnight')
       
        **do stuff**
        . 
        . 
        . 

if __name__ == "__main__": 

    # To use G0 stand alond
    p = om.Problem()
    p.model.add_subsystem('G0', AGroup())
    p.model.add_design_var('G0.X', lower=-1, upper=1)

    # To use G0 with some other component
    p = om.Problem()
    p.model.add_subsystem('some_comp', 
                          om.ExecComp('X=speed+3', units='furlongs/fortnight'))
    p.model.add_subsystem('G0', AGroup())
    p.model.connect('some_comp.X', 'G0.X')

    p.model.add_design_var('some_comp.speed', lower=-4, upper=-2)
```

Notice that there is no need to manually add an IndepVarComp anywhere in this model. 
The group level input is used as the design var directly in one case,
and connected into in another case. 
Underneath the covers, an IndepVarComp is added automatically and connected to the appropriate input. 


Description
===========
If you like your manually created IndepVarComps, you can keep them. 
However, the goal of this POEM is to make them largley obsolete.
This POEM proposes that all models, if they are a type of Group, would have an `_auto_ivc` component 
that will automatically create output variables for any inputs that were left unconnected after the 
setup process was completed. 

These automatically created variables will have automatically generated names, 
but users will not need to address those names ever. 
Instead changes will be made to variable name resolution (e.g. `prob['<some_var>']`) so that
no matter what name you specify (assuming it is a valid name) it will always be resolved to the associated output name. 
That will be true whether the associated output is one specified by your model via connection/promotion, 
or one automatically created in the `_auto_ivc` component. 


`_auto_ivc` output naming
-------------------------
To keep thing simple, and because in any normal usage the user will never have to directly address any 
auto_ivc outputs by their own name, the outputs of the `_auto_ivc` component will be named as: 
['v0', 'v1', 'v2', ... 'v<n>'] where `n` is 1 less than the number of unconnected input variables in 
the model after all user specified connections are resolved.

Variable Naming Paradigm
------------------------
As of V3.0 users address all outputs using their `promoted name` and all inputs using the `absolute name`.
Both the `promoted name` and the `absolute name` are unique (one points to the unique source, the other to the unique input). 
Most of the time, you can just set values using the `promoted name`.  However, if you use a `promoted name`,
that maps to multiple input variables but does not map to an output variable, then the framework raises an exception
because it's not clear which variable you're referring to.
To set the value for such inputs you must manually set the value to the absolute path of all the 
individual inputs that are promoted to the same name. 
If the inputs are unconnected, you can work around this by creating an IndepVarComp in the same group as the inputs, 
adding an output to it, and promoting that output to the same name as the input. 
Then you can set/get using the `promoted name`.  

POEM_015 will change this paradigm. 
Since there will be no unconnected inputs any more, every input variable will have a connected output variable as its source.
Every variable at every level of the hierarhcy will have a `natural_name`, which can always be resolved to a source. 
Users will set/get variables with any valid `natural_name`, 
and OpenMDAO will resolve that to the source name before performing the set/get operation on the source. 

Stated another way, setting a value using an input name will now result in updating the connected source, subject
to unit conversions and the value of src_indices on the input.  Similarly, getting a value using an
input name will retrieve the value of the connected source, again subject to unit conversions and
src_indices.

**Example:**
![example model to understand `natural name` vs `source name`](/POEM_015/poem_015_example_model.jpg)]

In this example, you have two components (`C0`, `C1`), down inside a group (`G0`). 
Both `C0` and `C1` have an input `X` which has been promoted up to the level of `G0`. 
Both component `C0` and `C1` have an output `Y`, but only `C1` has promoted that output to the level of `G0`. 

The following are all valid `natural_names` and matched up `source_names` for this model.

| `natural_name`| `source_name` |
|---------------|---------------|
| auto_ivc.v0   | auto_ivc.v0   |
| G0.X          | auto_ivc.v0   |
| G0.C0.X       | auto_ivc.v0   |
| G0.C1.X       | auto_ivc.v0   |
| G0.C0.Y       | G0.C0.Y       |
| G0.C1.Y       | G0.C1.Y       |
| G0.Y          | G0.C1.Y       |


Where the `_auto_ivc` component will live
----------------------------------------
All automatically created IVC outputs will live in the `_auto_ivc` component which will be added to 
the top level of any model, assuming that model is some type of Group.
This component will always be present in all models (even if there are no automatically created 
outputs), but should generally be invisible to the user. OpenMDAO will create explicit connections between 
any `_auto_ivc` output and its assocaited inputs. 


Resolving which unit should be applied
--------------------------------------

Though there are potentially many valid `natural_names` all pointing to the same source name, 
it is not required that all the inputs have the same units defined. 
When using the `Problem.__getitem__` and `Problem.__setitem__` (e.g. `prob['some_var'] = 3`) the 
unit will be matched to the specific unit defined with that `natural_name`. 

Consider the example from above. 
If `G0.C0.X` was defined in centimeters, and `G0.C1.X` was defined in meters then 
`prob['G0.C0.X'] = 3` will mean something different than `prob['G0.C1.X'] = 3`. 

To combat this, users can be more explicit via the `Problem.get_val` and `Problem.set_val` which 
allow for a `units=<something>` argument to be given so the intent is clear. 

Note: In OpenMDAO V3.0, users almost always set values using the `promoted_name` of the output, and 
the units that were assumed matched the output units. 
POEM_015 will not change this behavior. 
If you set/get using the equivalent `natural_name` to what would have been the `promoted_name` of 
any output variable In V3.0, then the infered units will still be the ones associated with the output. 

So with regard to inferred units when setting values, POEM_015 is 100% backwards compatible. 
It does however increase user options for how to set the value, 
since it will now be valid to set via any associated input name as well.
It is with this expanded ability to set values that users should take care, 
and why it will be recommended that you use the `set_val` and `get_val` methods if there is any 
possibility of ambiguitity. 

Dealing with natural names with `src_indices` associated with them
---------------------------------------------------------------------------

The proposed paradigm would normally resolve any natural name pointing to an input to the source name, 
then set the value into the memory for the source.
When there is a 1-to-1 correspondence in size between input and source, that can easily be done,
but when `src_indices` are given (during input declaration, or specified during connection/promotion) 
it can become more difficult. If the source maps to at least one input with 1-to-1 size correspondence,
then the framework will allow the connections of other inputs mapping to that source even if they have
src_indices. Otherwise the framework will raise an exception, and the user will have to use a
manually created IndepVarComp to connect to those inputs instead.


Setting defaults for unconnected promoted inputs in groups 
----------------------------------------------------------

In cases where the auto-ivc output connects to a single input, the value and unit of that output can 
be determined directly from the input. 
When there are two or more inputs promoted to a group level but nothing is connected to that promoted 
name, the units and value needed to create the auto-ivc output can become ambiguous if any of the 
values or units differ amongst the promoted set. 
In the case of any amiguity, users must call `group.set_input_defaults(...)` and provide the necessary 
default information required to create the auto-ivc output.  Otherwise an exception will be raised
at setup time.

There is another situation where `group.set_input_defaults` can be used to disambiguate access
to input variables via their promoted name.  When multiple inputs are promoted to the same name
and that promoted name is manually connected via the `connect` call to a non auto-ivc output,
the input defaults are not needed to create an auto-ivc output, but it can still be ambiguous if a 
user attempts to set/get using the promoted name if those inputs have different units.  In that 
situation, the framework will raise an exception at get/set time unless units have been provided by a
`group.set_input_defaults` call for that promoted input name.  Note that the exception doesn't
occur until get/set time, so the framework will allow the ambiguity to exist as long as the user
doesn't attempt to get/set using the ambiguous promoted input name.


Notes:

* `set_input_defaults` at the group level will accept the arguments `units` and `val`.
* calling `set_input_defaults` at a given group level will cause those defaults to be used for the
specified promoted input name at that group level as well as all corresponding promoted input
names above that group in the system hierarchy.  If `set_input_defaults` is called at different
levels in the system tree with promoted names that correspond to intersecting subsets of inputs,
the defaults specified in all of those calls must match or an exception will be raised.
* the unit information given in `set_input_defaults` will define the units used when setting/getting values using the promoted name.

Backwards Incompatible API Changes
----------------------------------

* If you have an any promoted but unconnected inputs with different values/units then you must call `set_input_defaults` at the group level. 
Otherwise an error will be thrown during setup, because the it is not possible to infer the units/value needed to create the auto_ivc output. 

* Previously, if you had a model with an unconnected promoted input at the group level, you could 
manually set the  values of each of the component inputs to a different value by addressing each 
one by its absolute name (i.e. its full path name). 
Now, when you set the value of any input by its full-path-name, you will also be setting the value 
of all other inputs to same value (or the equivalent value converted to the local units of the other inputs). 
(there doesn't seem to be any obvious reason why a user would have set inputs in this way,  but 
if you are doing that then you will see different behavior)


Implementations Details
---------------------

* This POEM will cause an increase in the amount of memory allocated, because there will be new space added to the output vector for the automatically created IVC outputs. 
* There will be additional data-transfers involved with the new automatically created IVC outputs, which will cause some additional overhead. 
The magnitude of these effects will depend on how many unconnected inputs you have but it is not expected to be large.
It is possible that some internal refactoring on the data-vectors may be able to mitigate the increased memory needs, but the additional data transfer will still be there. 
Before acceptance, some performance benchmarking will need to be performed to ensure performance remains high. 
* Because of the backwards incompatible change associated with `group.set_input_defaults`, we need to provide a smooth upgrade path for users.
So, as part of this implementation OpenMDAO would first release a version with `group.set_input_defaults` defined, but non-functional. 
Any unconnected-promoted inputs in the model would throw a deprecation warning, untill `group.set_input_defaults` was added for that group (or an IVC was manually connected to the promoted name). 
Users could upgrade to that version first, clear all the deprecation warnings, then be sure that the model would function properly under the next release which would include the auto-ivc functionality.
* The diagram and description of the variable naming paradigm in POEM_015 will be added to the docs. 
