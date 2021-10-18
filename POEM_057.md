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
by OpenMDAO.  This will sometimes be true if all of the function's inputs and outputs are scalar and
none of them have units, and there is no need to compute derivatives for the component.

If partials are added using the function wrapping API then the `method` specified in those partials
declarations will be used to compute the partials for the component.  If no partials are declared,
then all partials are assumed to be zero.


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
For `compute_partials`, the argument structure must follow that of the primary function followed by
a Jacobian object.   The Jacobian object is expected to be dict-like and
to take (of, wrt) name pairs as keys, with the corresponding sub-jacobian as the value for a given
key.  The shape of the expected sub-jacobian is determined by the shapes of the inputs and outputs and whether or not any rows and cols are given when the partials are declared, i.e., if rows and cols
are specified then the value stored in the jacobian will be only the nonzero part of that sub-jacobian. See POEM 056 for a description of how partials are declared for a function.

```python

def J_func(x, y, z, J): 

    # the following sub-jacs are 4x4 based on the sizes of foo, bar, x, and y, but the partials
    # were declared specifying rows and cols (in this case sub-jacs are diagonal), so we only
    # store the nonzero values of the sub-jacs, resulting in an actual size of 4 rather than 4x4.
    J['foo', 'x'] = -3*np.log(z)(3*x+2*y)**2 
    J['foo', 'y'] = -2*np.log(z)(3*x+2*y)**2 

    J['bar', 'x'] = 2.*np.ones(4)
    J['bar', 'y'] = np.ones(4)

    # z is a scalar so the true size of this sub-jac is 4x1
    J['foo', 'z'] = 1/(3*x+2*y) * 1./z


def func(x=np.zeros(4), y=np.ones(4), z=3): 
    foo = np.log(z)/(3*x+2*y)
    bar = 2.*x + y
    return foo, bar

f = (omf.wrap(func)
        .defaults(units='m')
        .add_output('foo', units='1/m', shape=4)
        .add_output('bar', shape=4)
        .declare_partials(of='foo', wrt=('x', 'y'), rows=np.arange(4), cols=np.arange(4))
        .declare_partials(of='foo', wrt='z')
        .declare_partials(of='bar', wrt=('x', 'y'), rows=np.arange(4), cols=np.arange(4)))

comp = om.ExplicitFuncComp(f, compute_partials=J_func)
```


## ImplicitFuncComp

Implicit components must have at least an `apply_nonlinear` method to compute the residual given 
values for input variables and implicit output variables (a.k.a state variables).  The mapping 
between a residual output and its corresponding state variable must be specified in the metadata 
when the output (state) is added.
 

```python

def implicit_resid(x, y):  # y is a state variable here
    R_y = y - tan(y**x)
    return R_y

f = (omf.wrap(implicit_resid)
        .add_output('y', resid='R_y'))  # y's corresponding resid is 'R_y'

comp = om.ImplicitFuncComp(f)
```


A `solve_nonlinear` method can also be specified as part of the metadata: 

```python

def implict_solve_nl(a, x, y):
    ...
    return x, y

def implicit_resid(a, x, y):  # a is input, x and y are states
    R_x = x + np.sin(a+y)
    R_y = y - tan(y)**x
    return R_x, R_y

f = (omf.wrap(implicit_resid)
        .add_output('x', resid='R_x')   # x's corresponding resid is 'R_x'
        .add_output('y', resid='R_y'))  # y's corresponding resid is 'R_y'

comp = om.ImplicitFuncComp(f, solve_nonlinear=implict_solve_nl)
```

### Providing a `linearize` and/or `apply_linear` for implicit functions

Implicit components use `linearize` and `apply_linear` methods to compute derivatives (instead of 
the analogous `compute_partials` and `compute_jacvec_product` methods in explicit components). 

```python

def func_linearize(x, y, J):  # x is input, y is output
    J['y', 'x'] = ...

def implicit_resid(x, y):
    R_y = y - tan(y**x)
    return R_y

f = (omf.wrap(implicit_resid)
        .add_output('y', resid='R_y'))  # y's corresponding resid is 'R_y'

comp = om.ImplicitFuncComp(f, linearize=func_linearize)
```
