POEM ID: 039  
Title: FuncComp  
authors: [@robfalck]  
Competing POEMs: 040  
Related POEMs: N/A  
Associated implementation PR:

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

To make the transition to OpenMDAO easier for users, it should be possible to allow OpenMDAO to wrap existing user-written functions with minimal input.

## Description

This POEM proposes a new function-wrapping component: FuncComp

The purpose of FuncComp is to allow users to wrap an existing Python function without first porting it to the compute-method of an ExplicitComponent.

### Determining input and output names

FuncComp should use `ast` or some other method to determine the names of the inputs to the function.

Outputs are more difficult.
First, there's no guarantee that return returns a variable, it may directly return the result of a calculation.
Secondly, functions may have multiple return statements.
FuncComp should use the final return in the outermost-scope to determine the number of return values from the function.
The output name should be via the following rules of precedence:

* the variable names returned, if it's possible to determine them
* `output` for a single unnamed return value
* `output_1`, `output_2`, etc. for multiple return values

### Variable metadata

Theres no way to associate units or shapes with normal Python inputs and outputs.
Docstrings can come in a variety of formats so relying on them to provide this information would likely be prohibitively restrictive.
After all, why make the user rewrite their docstring if the entire point of the component is to avoid having to rewrite their code.
Instead, we can use the same system that ExecComp uses where metadata is given via dictionaries passed as keyword arguments. 

### Differentiation

Differentiation should be supported via the standard OpenMDAO `declare_partials` API, which can be called on the instance 
after instantiation. 
Users can specify `<instance>.declare_partials('*', '*', method='cs')` or `<instance>.declare_partials('*', '*', method='fd')`. Alternatively, they can specify different settings for different variables if they wish. 
Using the standard OpenMDAO api gives the most flexibility. 

As a convenience, we can include an extra init argument for the class called `partials_method` which will default to `None`. If `None` then users are expected to declare their own partials using the standard API. However, if `cs` or `fd` then 
the class will call `<instance>.declare_partials('*', '*', method=<partials_method>)` for them. 

It should be an error if both `partials_method` and manual usage of the `declare_partials` api are used on the same instance. 

### Why ExecComp is insufficient for this purpose

Currently, there is no way for users to add their own functions into the executable scope of ExecComps. 
As an alternative to this approach we could allow users to register their own functions into the scope of ExecComps somehow. 
This would let users integrate their own functions into ExecComp. 

However, ExecComp was originally intended to be used for small and very cheap calculations and hence made a few simplifying assumptions about how derivatives would be computed. 
It uses **only** complex step (i.e. has no user configurable options for FD or fine grained control over step size and type). 
It also does not allow for any user declared coloring, instead offering a simplified coloring argument of **has_diag_partials** which indicates that all inputs and outputs are the same size (i.e. all sub-jacs are square) and have only diagonal entries. 
The simplified diagonal coloring is a very common occurence in exec-comps, which often do simple vectorized numpy calculations and allowing the user to directly specify the coloring this way saves OpenMDAO the difficulty/cost of coloring the component. 

It would be possible to modify the API to ExecComp to overcome these limitations, and hence provide this same functionality through ExecComp. 
This would yield a slightly different API than the one proposed here, but the functionality should be equivalent. 
An ExecComp based API for this feature is proposed in POEM_040. 

## Proposed API

`class FuncComp(om.ExplicitComponent)`

### Initialization

* The first argument should be a callable function.
* If this function has non-numeric input, it can be wrapped with a lambda to convert it to a function with only numeric inputs.
* Metadata for inputs and outputs will be provided with those variables as named arguments, the same way as it's done in ExecComp.
* both the `declare_partials` and `declare_coloring` methods will be user callable after instantiation

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

