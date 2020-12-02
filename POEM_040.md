POEM ID: 040  
Title: User Function Registration in ExecComp   
authors: [@justinsgray, @robfalck]  
Competing POEMs: 039  
Related POEMs: N/A  
Associated implementation PR:

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

Users find the ExecComp convenient, but its current library of functions is limited to a pre-defined set. 
If we let users register their own functions into that scope, they could compose much more complex components using the same syntax. 

This would greatly enhance the capability of ExecComp, and also allow users to more easily achieve common operations 
such as simple variable transformations of inputs via nested function calls. 

In addition, this new API would allow for a much simpler mechanism for users to wrap existing functional style python code into OpenMDAO without the need to write a lot of boiler plate class wrapper code. 


## Description

This POEM proposed to expand and enhance the ExecComp API to enable greater flexibility and simpler OpenMDAO model construction based on existing functional python code. 

Users will be able to register their own functions, and associated metadata, to the ExecComp scope and then will be able to use those functions in the same manner as any existing ExeComp functions. 

Users will also be able to exploit the new [size_by_connection](http://openmdao.org/twodocs/versions/3.4.1/features/experimental/dynamic_shapes.html) functionality that was introduced in OpenMDAO V3.4. 
NOTE: the size_by_connection is currently experimental. 
However, if this POEM is accepted, then that feature would be moved to officially supported status. 


### Function Registration API

NOTE: Though we are calling this a function registration, it should technically support any callable object. 

you can register new functions via the class method `register`: 

```python
ExecComp.register('<func_name>', some_callable_object, known_complex_safe=<False|True>)
```

The default for `known_complex_safe` is `False`, but users can set it to True. 
This argument controls whether a particular method will trigger the inclusion of any ExecComp instances that use it in the check_partials output. 

### Determining input and output names

I/O names are determined directly from the string expression passed to the ExecComp. 
This works identical to how ExecComps work now. 

### Determining input and output size 

Users can use the existing ExecComp API via kwargs to the constructor, to specify the sizes of all variables. 
However, two common cases are expected and will be supported by specific init args to ExecComp

1) If a user wants to have everything (both inputs and outputs) shaped by what they are connected to, then they can set the argument `shape_by_conn=True` and that metadata will be applied to every variables. 

2) If a user wants to have all inputs be the same size, because they are performing a vectorized operation, 
then they can set `vectorized=True` and all components will be the same size.
If they also set `shape_by_conn=True` then the sizes of all the inputs should be determined by their connections.
Their sizes should be compared to eachother. An error should be thrown if the inputs are not all the same size. 
Once it is known that all inputs are the same size, then the outputs can be sized to match the inputs. 

Note: Option #2 is important, so you can create chains of ExecComps that are all sized by a single upstream connection. 

### Differentiation

**This represents a change to the current ExecComp API**, but it is backwards compatible. 

Differentiation should be supported via the standard OpenMDAO `declare_partials` and `declare_coloring` APIs, which can be called on the ExecComp instance after instantiation. 
For example, users can specify `<instance>.declare_partials('*', '*', method='cs')` or `<instance>.declare_partials('*', '*', method='fd')`. Alternatively, they can specify different settings for different variables if they wish. 
Using the standard OpenMDAO api gives the most flexibility. 

We will also add a new init argument for the class,`partials_method`, which will default to ``partials_method='cs'` (to preserve backwards compatibility). If `partials_method='manual'` then users are expected to declare their own partials using the standard API. However, if ``partials_method='cs'` or ``partials_method='fd'` then 
the class will call `<instance>.declare_partials('*', '*', method=<partials_method>)` for them. 

It should be an error if both `partials_method` is not `'manual'` and the `declare_partials` or `declare_coloring` APIs are used on the same instance. 

### Partial Derivative Checking 

Hopefully in the vast majority of cases, users will use `partials_method='cs'`, since it is both accurate and fairly easy. 
It does require some extra care to make sure all methods are complex-safe though, so check_partials data is going to be needed on 
any ExecComp that includes the use of user registered method which are not known to be complex-safe. 

Currently, OpenMDAO internally skips all ExecComps whenever check_partials is called. 
This skip is reasonable, since the OM team takes ownership of the complex-safe-ness of all the internally registered methods. 

A user might develop a library of additional methods that they know are complex-safe. 
The registration API provides them the opportunity to mark any known-safe methods as such. 
This prevents excessive output in check partials that would be unneeded noise (which was why ExecComps were excluded in the first place)

If a user is just prototyping, or has not otherwise verified the CS-safeness of their method, then it should be included in the check. 
For any components that use `partials_method='cs'` and are included in the check_partials, 
the ExecComp should ensure that the verification method is finite difference. 
This will be done via the `set_check_partial_options` APIs. 


## Examples

### The user-defined function of a single variable

```python 
def area(x):
    return x**2

om.ExecComp.register('area', area)

om.ExecComp('area_square = area(x)', shape_by_conn=True)
```
The output is named `area_square` and the input is named `x`. 
Both are sized by the things they are connected to. 


### Functions with multiple outputs

```python
def aero_forces(rho, v, CD, CL, S)
    q = 0.5 * rho * v**2
    lift = q * CL * S
    drag = q * CD * S
    return lift, drag

om.ExecComp.register('aero_force', aero_forces)

om.ExecComp('L,D = aero_forces(rho, v, CD, CL, S)', 
             rho={'units': 'kg/m**3'},
             v={'units': 'm/s'},
             S={'units': 'm**2'},
             lift={'units': 'N'},
             drag={'units': 'N'}, 
             vectorized=True, shape_by_conn=True, has_diag_partials=True
            )
```

In this case, the output are named `L` and `D` and the inputs are named `rho`, `v`, `CD`, `CL`, `S`. 
No coloring is needed and the partials are computed using complex-step.
The sizes of the inputs are shaped by their connections, and the outputs are sized to match the inputs. 


### Nested function calls 
We can combine the `area` and `aero_forces` methods together into a single exec-comp, 
assuming they were both already registered. 

```python

om.ExecComp('L,D = aero_forces(rho, v, CD, CL, area(x))', 
             rho={'units': 'kg/m**3'},
             v={'units': 'm/s'},
             x={'units': 'm'},
             lift={'units': 'N'},
             drag={'units': 'N'}, 
             vectorized=True, shape_by_conn=True, has_diag_partials=True
            )
```

In this example, there is not component output for the `area` method. 
Instead of the `S` input there is now an `x` input. 



