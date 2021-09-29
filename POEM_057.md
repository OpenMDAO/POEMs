POEM ID: 057  
Title:  OpenMDAO function based components  
authors: [Bret Naylor]  
Competing POEMs:     
Related POEMs: 056   
Associated implementation PR:  

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

An OpenMDAO component that can provide an automatic way for a simple python function to be 
incorporated into a larger OpenMDAO model could be useful in a number of ways.  First, it could
provide an easy way to create a fully functional OpenMDAO component with minimal boilerplate code, serving a function similar to the existing `ExecComp` class.  Secondly, a plain python function 
interfaces more easily with existing AD libraries like `jax`, so it would be easier to use `jax` 
for example to compute the derivatives of this function wrapping component as opposed to a typical
OpenMDAO component.  Finally, it may be possible to leverage, with minimal effort, existing python 
code from other engineering applications as long as it is implemented as simple python functions.

This POEM will discuss two component classes; `ExplicitFuncComp`, based on OpenMDAO's 
`ExplicitComponent`, and `ImplicitFuncComp`, based on `ImplicitComponent`.

This POEM makes heavy use of the function wrapping API described in POEM 056.


## Common behavior

Both component types are intended to work with an instance of `OMWrappedFunc` which wraps a plain
python function.  Passing a plain python function directly to the `__init__` function of 
`ExplicitFuncComp` or `ImplicitFuncComp` is allowed as long as no additional metadata is needed
by OpenMDAO.  This will often be true if all of the function's inputs and outputs are scalar and
none of them have units.

If partials were added using the function wrapping API then the `method` specified in those partials
declarations will be used to compute the partials for the component.  If no partials were declared,
then dense partials based on full variable dependencies between outputs and inputs of the function 
will be declared automatically, and complex step will be used to compute the partials, similarly to 
what is currently done in the `ExecComp`.


## ExplicitFuncComp

In most cases, any metadata needed to construct the `ExplicitFuncComp` has already been attached
to the function object using the previously mentioned function wrapping API, so all that's needed
to create the component is the following:

```python

# func has been previously defined using the function wrapping API...

comp = om.ExplicitFuncComp(func)

```

### Providing a `compute_partials`

Users can provide a second function that gives `compute_partials` functionality. 
For `compute_partials`, the argument structure must follow that of the primary function, with one
additional argument: a Jacobian object.   The Jacobian object is expected to be dict like and
to take an (of, wrt) name pair as a key, with the corresponding sub-jacobian as the value for that
key.  The shape of the expected sub-jacobian is determined by the shapes of the inputs and outputs and whether or not any rows and cols are given when the partials are declared, i.e., if rows and cols
are specified then the value stored in the jacobian will be only the nonzero part of that sub-jacobian. See POEM 056 for a description of how partials are declared for a function.

```python

def J_func(x, y, z, J): 

    J['foo', 'x'] = -3*np.log(z)(3*x+2*y)**2 
    J['foo', 'y'] = -2*np.log(z)(3*x+2*y)**2 
    J['foo', 'z'] = 1/(3*x+2*y) * 1/z

    J['bar', 'x'][:] = 2
    J['bar', 'y'][:] = 1

def func(x=np.zeros(4), y=np.ones(4), z=3): 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

f = (omf.wrap(func)
        .defaults(units='m')
        .add_input('z', units=None)
        .add_output('foo', units='1/m', shape=4)
        .add_output('bar', shape=4)
        .declare_partials(of='foo', wrt='*', rows=np.arange(4), cols=np.arange(4))
        .declare_partials(of='bar', wrt=('x', 'y'), rows=np.arange(4), cols=np.arange(4)))

comp = om.ExplicitFuncComp(f, compute_partials=J_func)
```

### Providing a jacobian vector product function

Just like a normal explicit component, if you are using the matrix free API then you should not 
declare any partials.  The matrix vector product method signature will expect three additional arguments added beyond those in the nonlinear function: `d_inputs`, the array of input derivatives,
`d_outputs`, the array of output derivatives, and `mode`, which indicates derivative direction,
either `fwd` or `rev`.

```python

def jac_vec_func(x, y, z, d_inputs, d_outputs, mode):
    ...  

# func is some wrapped function with inputs x, y, and z
comp = om.ExplicitFuncComp(func, compute_jacvec_product=jac_vec_func)
```


## ImplicitFuncComp

Implicit components must have at least an `apply_nonlinear` method to compute the residual given 
values for input variables and implicit output variables (a.k.a state variables).  The mapping 
between a residual output and its corresponding state variable must be specified in the metadata 
when the output is added.
 

```python

def implicit_resid(x, y):  # y is a state variable here
    R_y = y - tan(y**x)
    return R_y

f = (omf.wrap(implicit_resid)
        .add_output('R_y', state='y'))  # R_y's corresponding state is 'y'

comp = om.ImplicitFuncComp(f)
```


A `solve_nonlinear` method can also be specified as part of the metadata: 

```python

def implict_solve(x, y):
    ...

def implicit_resid(x, y):
    R_x = x + np.sin(x+y)
    R_y = y - tan(y)**x
    return R_x, R_y

f = (omf.wrap(implicit_resid)
        .add_output('R_x', state='x')   # R_x's corresponding state is 'x'
        .add_output('R_y', state='y'))  # R_y's corresponding state is 'y'

comp = om.ImplicitFuncComp(f, solve_nonlinear=implicit_solve)
```

### Providing a `linearize` and/or `apply_linear` for implicit functions

Implicit components use `linearize` and `apply_linear` methods to compute derivatives (instead of 
the analogous `compute_partials` and `compute_jacvec_product` methods in explicit components). 

```python

def func_linearize(x, y, J): 
    ... 

def some_implicit_resid(x, y):
    R_y = y - tan(y**x)
    return R_y

f = (omf.wrap(implicit_resid)
        .add_output('R_y', state='y'))  # R_y's corresponding state is 'y'

comp = om.ImplicitFuncComp(f, linearize=func_linearize)
```
