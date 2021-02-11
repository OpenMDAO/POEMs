POEM ID: 039  
Title: User Function Registration in ExecComp   
authors: [@justinsgray, @robfalck]  
Competing POEMs: N/A    
Related POEMs: N/A   
Associated implementation PR:

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation

Users find the ExecComp convenient, but its current library of functions is limited to a pre-defined set. 
If we let users register their own functions into that scope, they could compose much more complex components using the same syntax. 

This would greatly enhance the capability of ExecComp, and also allow users to more easily achieve common operations 
such as simple variable transformations of inputs via nested function calls. 

In addition, this new API would allow for a much simpler mechanism for users to wrap existing functional style python code into OpenMDAO without the need to write a lot of boiler plate class wrapper code. 


## Description

This POEM proposed to expand and enhance the ExecComp API to enable greater flexibility and simpler OpenMDAO model construction based on existing functional python code. 

Users will be able to register their own functions and use them in the same manner as any existing ExeComp functions. 

Users will also be able to exploit the new [shape_by_conn](http://openmdao.org/twodocs/versions/3.4.1/features/experimental/dynamic_shapes.html) functionality that was introduced in OpenMDAO V3.4. 
NOTE: the shape_by_conn is currently experimental. 
However, if this POEM is accepted, then that feature would be moved to officially supported status. 


### Function Registration API

NOTE: Though we are calling this a function registration, it should technically support any callable object. 

you can register new functions via the class method `register`: 

```python
ExecComp.register(name, callable_object, complex_safe)
```

Note that the complex_safe argument is required in order to tell the framework whether the
function is complex safe or not.  This will determine which approximation schemes are allowed,
and whether or not derivatives for ExecComps using that function will be visible by default
when calling `check_partials`.

### Determining input and output names

I/O names are determined directly from the string expression(s) passed to the ExecComp. 
This works identical to how ExecComps work now. 

### Determining input and output size 

Users can use the existing ExecComp API via kwargs to the constructor, to specify the shapes of all variables. 
However, four common cases are expected and will be supported by specific init args to ExecComp

1) If a user wants to have everything (both inputs and outputs) shaped by what they are connected to, then they can set the argument `shape_by_conn=True` and that metadata will be applied to every variables. 

2) If a user wants to have all inputs be the same size,
then they can set `shape=<value or variable>` to set the shape of all the inputs and outputs. 
If they need to make the shape some kind of user configurable value, then that can be added to the owning group as an option. 


Note: Ideally, it would be possible to set shape of the inputs based on what they are connected to and then have the output shapes computed based on that. 
There are some ways to make this work, but they are ad-hoc and not general enough to be worth adding at this time. 
Adding the ability for components to cascade their size as they compute should be the subject of a separate (and more general) POEM that deals with more than just ExecComp. 

### Differentiation

The exec-comp does all differentiation through complex-step, but via a different chunk of code than the normal OpenMDAO CS approximation. 
This is done to provide accurate derivatives via complex-step, but also to provide some customization for the `has_diag_partials` option, which provides for a common and very simple partial derivative coloring case. 
Currently, all functions provided in the ExecComp have been checked by the dev team to be complex-safe. 
However, this POEM will allow users to register their own functions, which may or may not be complex-safe. 

One option would be to let users select a finite-difference option (instead of complex-step), however this introduces several significant complexities. 
First and foremost, FD is much more sensitive to FD step size and FD method (e.g. forward, central, backward). 
So allowing users to select FD really should also mean they have an API to change those settings. 
OpenMDAO components already provide this API via the `decalre_partials` method (and an associated `declare_coloring` method.
The purpose of `ExecComp` is to provide a lightweight and low line-of-code way of interacting with functions, 
so requiring users to add multiple extra lines to declare their partials may defeat the purpose of this feature. 

So, by default ExecComp will retain its internal CS behavior. 
Users may override this by calling `declare_partials` and/or `declare_coloring` on the component, 
but doing this will turn off all internal/default CS code and will instead use the standard OpenMDAO component approximation tools. 
So by calling `declare_partials` for anything, a user is implicitly agreeing to define the partials for that entire component. 

This approach offers two key benefits. 
First it is backwards compatible and retains the compact usage style current to ExecComp. 
Second it gives users who don't want to use complex-step a means of using finite-difference instead, and they can retain most of the functionality from `has_diag_partials` via the `declare_coloring` API instead. 

### Partial Derivative Checking 

Hopefully in the vast majority of cases, users will use ExecComp's built-in 'cs' implementation, since it is both accurate and fairly easy. 
It does require some extra care to make sure all methods are complex-safe though, so check_partials data is going to be needed on 
any ExecComp that includes the use of user registered methods which are not known to be complex-safe. 

Currently, OpenMDAO skips all ExecComps whenever check_partials is called. 
This skip is reasonable, since the OM team takes ownership of the complex-safe-ness of all the internally registered methods. 

A user might develop a library of additional methods that they know are complex-safe. 
The registration API provides them the opportunity to mark any complex safe methods as such by providing the `complex_safe` argument.
Setting `complex_safe` to True allows the use of complex step and also prevents excessive output in check partials that would be unneeded noise (which was why ExecComps were excluded in the first place).  

If a user is just prototyping, or has not otherwise verified the CS-safeness of their method, then it will be included in the check. 
For any ExecComps that use complex step and are included in the check_partials, 
the ExecComp should ensure that the verification method is finite difference. 
This will be done via the `set_check_partial_options` APIs. 

If an ExecComp references a complex unsafe function then
any inputs on the right hand side of the expression referencing that function must have their partials declared to use 'fd'
or an exception will be raised.


## Examples

### The user-defined function of a single variable

```python 
def area(x):
    return x**2

om.ExecComp.register('area', area, complex_safe=True)

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

om.ExecComp.register('aero_force', aero_forces, complex_safe=True)

om.ExecComp('L,D = aero_forces(rho, v, CD, CL, S)', 
             rho={'units': 'kg/m**3'},
             v={'units': 'm/s'},
             S={'units': 'm**2'},
             lift={'units': 'N'},
             drag={'units': 'N'}, 
             has_diag_partials=True, shape=nn
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
             has_diag_partials=True
            )
```

In this example, there is not component output for the `area` method. 
Instead of the `S` input there is now an `x` input. 



