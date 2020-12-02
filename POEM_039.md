POEM ID: 039
Title: FuncComp
authors: [@robfalck]
Competing POEMs: N/A  
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

The purpose of FuncComp is to allow users to wrap an existing Python function without first porting it to the compute-method of an ExplicitComponent.1

### Determining input and output names

FuncComp should use `ast` or some other method to determine the names of the inputs to the function.

Outputs are more difficult.
First, there's no guarantee that return returns a variable, it may directly return the result of a calculation.
Secondly, functions may have multiple return statements.
FuncComp should use the final return in the outermost-scope to determine the number of return values from the function.
The output name should be as follows:

* the variable names returned, if it's possible to determine them
* `output` for a single unnamed return value
* `output_1`, `output_2`, etc. for multiple return values

### Variable metadata

Theres no way to associate units or shapes with normal Python inputs and outputs.
Since docstrings can come in a variety of formats, relying on docstrings to provide this information would likely be prohibitively restrictive.
After all, why make the user rewrite their docstring if the entire point of the component is to avoid having to rewrite their code.
Variable metadata will be provided via a keyword argument (the variable name) and a dictionary of the associated metadata.
This is the same approach used by ExecComp.

### Differentiation

Initially, FuncComp should support differentiation of the wrapped function via complex-step, with a fallback to finite-differencing if the wrapped function is not complex-compatible.1

In time, the use of automatic differentiation (AD) via jax or some other tool should be considered.  However, the wrapped function may itself call a multitude of other functions, which could make AD difficult.

### Why ExecComp is insufficient for this purpose

ExecComp is fundamentally about writing a small set of equations as a component without the need to define it as a full-blown ExplicitComponent.
Typically, user-defined functions contain many lines of interrelated code, rather than the simple expressions used in ExecComp.
FuncComp will let users wrap functions of arbitrary complexity and approximate the partials across them with complex-step, finite-differencing, and eventually (possibly) AD.

## Proposed API

`class FuncComp(om.ExplicitComponent)`

### Initialization

* The first argument should be a callable function.
* If this function has non-numeric input, it can be wrapped with a lambda to convert it to a function with only numeric inputs.
* Metadata for inputs and outputs will be provided with those variables as named arguments, the same way as it's done in ExecComp.
* Argument **approx_partials**, will accept 'cs' or 'fd', to specify the method for approximating partials and default to 'cs'
* Argument **declare_coloring** should provide a dictionary containing the arguments to the declare_coloring method for the component, and default to None.

## Examples

### The user-defined function of a single variable

```
def area(x):
    return x**2

FuncComp(area,
         x={'units': 'm', shape=(10,)},
         output={'units': 'm**2', shape=(10,)},
         declare_coloring={'wrt': '*', 'method': 'cs', 'tol': 1.0E-8, 'show_sparsity': True})
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

FuncComp(aero_forces,
         rho={'units': 'kg/m**3'},
         v={'units': 'm/s'},
         S={'units': 'm**2'}
         lift={'units': 'N'},
         drag={'units': 'N'})
```

In this case, the output names may be inferred from the return statement.
No coloring is needed and the partials are computed using complex-step, the default.

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


