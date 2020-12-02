POEM ID: 040  
Title: User Function Registration in ExecComp   
authors: [@justinsgray]  
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


#### Sizing Variables and other MetaData
Situations that we need to consider: 
1) functions with a fixed i/o size
2) vectorized functions where all I/O is the same size (but the size could vary from one usage to another)
3) all I/O is sized by connection 
4) Situation where some variables are fixed size and some are shaped by connection


For case #1, the exact same APIs that already exist for sizing variables in ExecComp. 
Each kwarg given to the registration function must match a kwarg in the function itself (this should be verified by AST during registration). 
For each kwarg given to the registration user can pass a value (from which size is inferred) or a dictionary of metadata. 

Note this will be done during the registration, and hence can be done one time and the meta-data is held as the defaults for that method. 
Users could choose to override the variable meta-data in a specific exec-comp later on if they wish, but the registration metadata will be the default. 
```python
exec_func = om.reg_exec_comp_func('<func_name>', some_callable_object, <kwarg_1>=<meta_data>, <kwarg_2>=<meta_data>, )
```
```python
exec_func = om.reg_exec_comp_func('<func_name>', some_callable_object, units='km', shape=3 )
```

For case #2, the user will pass the we can rely on `shape_by_conn` and `copy_shape` arguments to `add_input` so that all outputs will copy the shape of one of the inputs. 
It should not matter which input shape is copied, since they must all be the same size. 
User will pass the `vectorized` argument to the `reg_exec_comp_func` method to indicate this situation. 
Other metadata (i.e. units) can still be passed. In addition user could provide size and value metadata to serve as defaults that are used when no connections are made. 
```python 
exec_func = om.reg_exec_comp_func('<func_name>', some_callable_object, vectorized=True, <kwarg_1>=<meta_data>, <kwarg_2>=<meta_data>)
```

For case #3, the we rely only on the `shape_by_conn` argument to `add_input`. 
In this case the inputs are sized by their connections and the outputs by theirs.
```python 
exec_func = om.reg_exec_comp_func('<func_name>', some_callable_object, shape_by_conn=True, <kwarg_1>=<meta_data>, <kwarg_2>=<meta_data>)
```

For case#4, we allow the user to add the specific sizing method to the metadata for the appropriate arguments. 
This would look identical to case 1, but with the appropriate sizing arguments added to the metadata


### Determining input and output names

I/O names are determined directly from the string expression passed to the ExecComp. 
This works identical to how ExecComps work now. 

### Differentiation

**This represents a change to the current ExecComp API**, but it can be made backwards compatible. 

Differentiation should be supported via the standard OpenMDAO `declare_partials` API, which can be called on the instance 
after instantiation. 
Users can specify `<instance>.declare_partials('*', '*', method='cs')` or `<instance>.declare_partials('*', '*', method='fd')`. Alternatively, they can specify different settings for different variables if they wish. 
Using the standard OpenMDAO api gives the most flexibility. 



As a convenience, we can include an extra init argument for the class called `partials_method` which will default to `CS` (to preserve backwards compatibility). If `None` then users are expected to declare their own partials using the standard API. However, if `cs` or `fd` then 
the class will call `<instance>.declare_partials('*', '*', method=<partials_method>)` for them. 

It should be an error if both `partials_method` and manual usage of the `declare_partials` api are used on the same instance. 



## Examples

### The user-defined function of a single variable

```
def area(x):
    return x**2

fc = FuncComp(area,
         x={'units': 'm', shape=(10,)},
         output={'units': 'm**2', shape=(10,)}) 
fc.declare_coloring(wrt='*', method='cs', tol=1.0E-8, show_sparsity=True})
```

In this case, introspection can't determine the name of the output, so the single output is simply 'output'.
This case is contrived, and there's a significant amount of boilerplate here to make this simple function work, ExecComp would be a better choice in this instance.declare_coloring

### A slightly more complex function

```
def aero_forces(rho, v, CD, CL, S)
    q = 0.5 * rho * v**2
    lift = q * CL * S
    drag = q * CD * S
    return lift, drag

FuncComp(aero_forces, partials_method='cs', 
         rho={'units': 'kg/m**3'},
         v={'units': 'm/s'},
         S={'units': 'm**2'}
         lift={'units': 'N'},
         drag={'units': 'N'})
```

In this case, the output names may be inferred from the return statement.
No coloring is needed and the partials are computed using complex-step.

### Using lambda to wrap functions with non-numeric arguments

In this case we're wrapping scipy's `det` function, which computes the determinant of a matrix.
In this case, the function takes two boolean arguments that we want to omit from the wrapped component's IO.

The signature of the function is:

```
scipy.linalg.det(a, overwrite_a=False, check_finite=True)
```

It can be wrapped using a lambda like this:

```
FuncComp(lambda a: scipy.linalg.det(a, overwrite_aFalse, check_finite=True),
         a={'units': None, 'shape': (3, 3)})
```

## Open Issues

It may be difficult to determine ahead of time what outputs were discovered for a given function.
Were variable names automatically determined?

It might be useful to find a different way to specify outputs.  Perhaps they should always be named `output_1`, `output_2`, etc.

