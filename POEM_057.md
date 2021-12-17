POEM ID: 057  
Title:  OpenMDAO function based components  
authors: [Bret Naylor]  
Competing POEMs:     
Related POEMs: 056   
Associated implementation PR: [#2309](https://github.com/OpenMDAO/OpenMDAO/pull/2309)

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


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

### Matrix free operation

Users can also provide a function analagous to the `compute_jacvec_product` method on openmdao
components that will compute a jacobian vector product in fwd mode or a vector jacobian product 
in rev mode.  This allows derivatives to be computed without allocating space for the full jacobian. 
The order of the args is input0, ... input_n, followed by d_input0, ... d_input_n, followed by
d_output0, ... d_output_n, followed by mode and lin_data.  Also, if a given d_() arg is not relevant 
its value will be set to `None`.


```python

def jvp_func(input0, ..., input_n, d_input0, ..., d_input_n, d_output0, ... d_output_n, 
             mode, lin_data):
    if mode == 'fwd':
        # do stuff
        return d_outputs0, ... d_outputs_n

    if mode == 'rev':
        # do stuff
        return d_inputs0, ... d_inputs_n

comp = om.ExplicitFuncComp(f, compute_jacvec_product=jvp_func)

```

## ImplicitFuncComp

Implicit components must have at least an `apply_nonlinear` method to compute the residual given 
values for input variables and implicit output variables (a.k.a state variables).  The mapping 
between a state and its residual output must be specified in the metadata when the output (state) 
is added by setting 'resid' to the name of the residual.

It may seem confusing to use `add_output` to specify state variables since the state variables
are actually inputs to the function, but in OpenMDAO's view of the world, states are outputs so
we use `add_output` to specify them.  Also, using the metadata to specify which inputs are
actually states gives more flexibility in terms of how the function arguments are ordered.
For example, if it's desirable for a function to be passable to `scipy.optimize.newton`, then
the function's arguments can be ordered with the states first, followed by the inputs, in order
to match the order expected by `scipy.optimize.newton`.
 

```python

def apply_nl(y, x):  # y is a state variable here
    R_y = y - tan(y**x)
    return R_y

f = (omf.wrap(apply_nl)
        # States are specified by setting the corresponding resid
        .add_output('y', resid='R_y'))  # y is a state, with corresponding resid 'R_y'

comp = om.ImplicitFuncComp(f)
```


### Providing additional methods to the ImplicitFuncComp

Other functions in addition to the `apply_nonlinear` function can be specified to add 
functionality to the ImplicitFuncComp.


A `solve_nonlinear` method can also be passed in to the `ImplicitFuncComp`: 

```python

def solve_nl(a, x, y):
    ...
    return x, y

def implicit_resid(a, x, y):  # a is input, x and y are states
    R_x = x + np.sin(a+y)
    R_y = y - tan(y)**x
    return R_x, R_y

f = (omf.wrap(implicit_resid)
        .add_output('x', resid='R_x')   # x's corresponding resid is 'R_x'
        .add_output('y', resid='R_y'))  # y's corresponding resid is 'R_y'

comp = om.ImplicitFuncComp(f, solve_nonlinear=solve_nl)
```

A `linearize` method can be provided to compute a partial derivative jacobian.  The return value of
`linearize` will be passed on to a user-provided `solve_linear` function, if it exists.
Below is an example of defining an ImplicitFunction comp for a simple linear system that defines
a custom `linearize` and `solve_linear`.

```python

x = np.array([1, 2, -3])
A = np.array([[1., 1., 1.], [1., 2., 3.], [0., 1., 3.]])
b = A.dot(x)

def apply_nl(A, b, x):
    rx = A.dot(x) - b
    return rx

# in the linearize func we populate the sub-jacobians of the partial jacobian J.
# note that all of our sub-jacobians are sparse in this case (based on our setting of rows
# and cols in the declare_partials calls below) so we only set the nonzero values.  This behavior
# matches what happens in the `linearize` method in the OpenMDAO component API.
def linearize_func(A, b, x, J):
    J['x', 'A'] = np.tile(x, 3).flat
    J['x', 'x'] = A.flat
    J['x', 'b'] = np.full(3, -1.0)

    # return LU decomp for use later in solve_linear
    return linalg.lu_factor(A)


# d_x here will be either d_residuals['x'] in fwd mode or d_outputs['x'] in rev mode
# linearize_return_val is what we returned from the last call to linearize_func
def solve_linear_func(d_x, mode, linearize_return_val):
    if mode == 'fwd':
        return linalg.lu_solve(linearize_return_val, d_x, trans=0)
    else:  # rev
        return linalg.lu_solve(linearize_return_val, d_x, trans=1)


# here we wrap the apply_nl function and attach metadata needed by OpenMDAO to it.
f = (omf.wrap(apply_nl)
        .add_input('A', val=A)
        .add_input('b', val=b)
        .add_output('x', resid='rx', val=x)
        .declare_partials(of='x', wrt='b', rows=np.arange(3), cols=np.arange(3))
        .declare_partials(of='x', wrt='A', rows=np.repeat(np.arange(3), 3), cols=np.arange(9))
        .declare_partials(of='x', wrt='x', rows=np.repeat(np.arange(3), 3), cols=np.tile(np.arange(3), 3)))

comp = om.ImplicitFuncComp(f, linearize=linearize_func, solve_linear=solve_linear_func)
```

Users can also provide an `apply_linear` function that will compute a jacobian vector product in 
fwd mode or a vector jacobian product in rev mode.  This will allow derivatives to be computed
without allocating space for the full jacobian. The order of the args is determined by the order 
of the args of the `apply_nonlinear` function. In the case below, the `apply_linear` args were 
output0, ... output_n, input0, ... input_n, so the args to the `apply_linear` funcion are those 
same args, followed by d_(those same args), followed by d_resid(just the output args), followed by 
mode and lin_data.  Also, if a given d_() arg or d_resid() arg is not relevant its value will be 
set to `None`.

```python

def apply_linear_func(output0, ... output_n, input0, ..., input_n, d_output0, ... d_output_n, 
                      d_input0, ..., d_input_n, d_resid0, .. d_resid_n, mode, lin_data):
    if mode == 'fwd':
        # do stuff
        return d_resid0, ..., d_resid_n

    else:  # rev
        # do stuff
        return d_output0, ... d_output_n, d_input0, ... d_input_n


comp = om.ImplicitFuncComp(f, apply_linear=apply_linear_func)

```
