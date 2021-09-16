POEM ID: 052  
Title:  Function based component definition for OpenMDAO  
authors: [justinsgray, Ben Margolis, Kenny Lyons, Bret Naylor]  
Competing POEMs: N/A    
Related POEMs: 039   
Associated implementation PR:  

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

Define an OpenMDAO component, including all I/O with metadata, the compute method, and potentially 
derivatives using a function based syntax. 

## Explicit API Description

A function based syntax for component definition has several nice properties. It offers a fairly 
compact syntax, especially in cases where there is uniform metadata for all I/O in the component. 
It also provides an interface that is more compatible with algorithmic differentiation than the 
traditional dictionary-like arguments to the `compute` method of the standard OpenMDAO API. 

The proposed functional component API in this POEM was inspired by the function registration API in POEM_039, 
but seeks to extend that concept further to allow full component definitions using a python function definition. 
Since Python 3.0, the language has supported function annotations which can be used to provide metadata 
that a special component can interrogate and then wrap in the normal OpenMDAO API. 

Here is a verbose example of the proposed API for a function with three inputs (`x,y,z`) and two 
outputs (`foo,bar`).  In this case, all inputs have default values (which also provide shape information) and
units, and return value annotations are provided to specify output names and output shapes and units.


```python
def some_func(x:{'units':'m'}=np.zeros(4), y:{'units':'m'}=np.ones(4), z=3) -> [('foo', {'units':'1/m', 'shape':4}), 
                                                                                ('bar', {'units':'m', 'shape':4})]:
    return np.log(z)/(3*x+2*y),  2*x+y
```

### Why return annodations must sometimes provide output names 

While the names of the inputs are guaranteed to be able to be introspected from the function definition, 
the same is not true for return values.  In the example above, there is no way to infer output
names because the return values are expressions rather than local variables.
Hence output variable names have to be given as part of the function annotation in this case.  
However, if a function's return values are simply local variables then it is possible to infer
their corresponding output names.  For example:

```python
def some_func(x=np.zeros(4), y=np.ones(4), z=3):
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

In the example above, the function can be expressed concisely because the inputs and outputs
have no specified units.  The only critical bit of information needed to fully define the
function component is the shapes on the inputs and outputs.  The input shapes are computed from
the provided default values.  The output shapes are computed, based on those input shapes, by
the `jax` package.  Note that if the `jax` package is not installed, the shapes of the outputs
would have to be provided via annotation. For example:

```python
def some_func(x=np.zeros(4), y=np.ones(4), z=3) -> [('foo', {'shape': 4}), ('bar', {'shape': 4})]:
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

Also note that installing the `jax` package does not automatically cause AD to be used to compute
the derivatives of the function, but it will allow output shapes to be automatically determined
based on input shapes for functions that `jax` is able to trace.  If the `jax` trace fails for
any reason and the return values shapes are not specified in the annotation then an exception will
be raised since the output shapes cannot be determined.


### Return annotations must be a list of (<var_name>, <var_meta>) tuples

The API provides output annotations in a strictly ordered data structure so that the metadata can be
matched with the correct return value, so return annotations must be a list of 
(<var_name>, <var_meta>) tuples as shown above.  Note that for any return value annotation entry,
the <var_name> part of each tuple is always required even if, as in the example above, the name
could be determined automatically.


### Shorthand for uniform metadata 
Using the `func_meta` function decorator, we can specify function metadata like default values for 
units and shape. This allows for a more compact syntax by eliminating repetition of metadata entries 
for each input and output variable.

```python
@om.func_meta(default_units='m', default_shape=4)
def uniform_meta_func(x, y, z): 
    foo = x+y+z
    bar = 2*x+y
    baz = 42*foo
    return foo, bar, baz
```

Any variable or return value annotations provided in the function definition will take precedence 
over the ones given in the decorator.

### Variable sizing 

One unique aspect of OpenMDAO variable metadata syntax is that you can specify a scalar default value 
and a shape, and OpenMDAO interprets that to mean `np.ones(shape)*default_val`. 
For consistency, the functional API will respect the convention. 
If `shape` is given as metadata, then the default value will be broadcast out to that shape as long
as the default value is scalar. If `shape` metadata is given along with a non-scalar default value 
for the argument, then an exception will be raised during setup by OpenMDAO. If `shape` metadata is given 
without any default value, then a default value of `np.ones(shape)` will be assumed, and if no `shape` or
default value is provided, a default value of `1.0` will be assumed.

```python
def some_func(x:{'shape':4}=0., y:{'shape':4}=1., z=3) -> [('foo',{'shape':4}), ('bar',{'shape':4})] : 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

In the example above, the actual default value for `x` would be `np.zeros(4)` and for `y` it
would be `np.ones(4)`.


## Adding a FuncComponent to a model 
OpenMDAO will add a new Component to the standard library called `ExplicitFuncComp`, which will accept 
one or more functions as arguments and will then create the necessary component and all associated I/O.

```python
def func(x:{'shape':4}, y:{'shape':4}, z=3.): 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(func)
```

The resulting `comp` component instance would have three inputs: `x`, `y`, and `z`, 
and two outputs, `foo` and `bar`. 


## Providing partial derivatives

Because ExplicitFuncComp is an OpenMDAO component, users will have access to the full `declare_partials`  
API, including specifying any details about finite difference or complex-step approximations and can
also use the `declare_coloring` component API. 

If users want to potentially reuse their function in multiple ExplicitFuncComps, they can associate
metadata with their function that OpenMDAO can use to properly set up computation of partial 
derivatives for any ExplicitFuncComp using that function.

This can be accomplished using the `declare_partials` and `declare_coloring` decorators.

### Using `declare_partials` and `declare_coloring`

```python

@om.declare_partials(of='*', wrt='*', method='cs')
@om.declare_coloring(wrt='*', method='cs')
def func(x=np.zeros(4), y=np.ones(4), z=3) -> [('foo':{'shape':4}), ('bar',{'shape':4})]: 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(func)
```

The args for the `declare_partials` and `declare_coloring` decorators exactly match those
of the  `declare_partials` and `declare_coloring` methods of an OpenMDAO component.  Multiple calls
can be made to either decorator to set up different partials/colorings.  The partials will be
ordered top to bottom, just as they would be if the corresponding methods were called on a
component.


### Providing a `compute_partials`

Users can provide a secondary function that gives `compute_partials` functionality.  
For `compute_partials`, the input arguments must be in the same order as those of the primary function, 
followed by one additional argument which is the provided Jacobian object. 
Just like a normal OpenMDAO component, the shape of the expected derivative data is determined by 
the shapes of the inputs and outputs and whether or not any rows and cols are given.  So, for
example in `J_func` below, because the partial of `foo` with respect to `x` is defined as 
diagonal (due to the values set for `rows` and `cols`), the shape of the array being assigned
to J['foo', 'x'] is 4 rather than what would be its 'true' size, which is (4, 4) because we're
only setting the nonzero elements.

```python

def J_func(x, y, z, J): 

    J['foo', 'x'] = -3*np.log(z)(3*x+2*y)**2 
    J['foo', 'y'] = -2*np.log(z)(3*x+2*y)**2 
    J['foo', 'z'] = 1/(3*x+2*y) * 1/z

    J['bar', 'x'][:] = 2 # need to set all elements of array
    J['bar', 'y'][:] = 1 # need to set all elements of array


@om.declare_partials(of='foo', wrt='*', rows=np.arange(4), cols=np.arange(4))
@om.declare_partials(of='bar', wrt=('x', 'y'), rows=np.arange(4), cols=np.arange(4))
def func(x:{'units':'m'}=np.zeros(4), y:{'units':'m'}=np.ones(4), z=3) -> [('foo',{'units':'1/m', 'shape':4}), 
                                                                           ('bar',{'units':'m', 'shape':4})]: 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(func, compute_partials=J_func)
```

### Providing a `compute_jacvec_product`

Just like a normal explicit component, if you are using the matrix free API then you should not 
declare any partials. The matrix vector product method method signature will expect three additional 
arguments added beyond those in the nonlinear function: `d_inputs, d_outputs, mode` 

```python

def jac_vec_func(x, y, z, d_inputs, d_outputs, mode):
    ...  

def some_func(x:{'units':'m'}=np.zeros(4), y:{'units':'m'}=np.ones(4), z=3) -> [('foo',{'units':'1/m', 'shape':4}), 
                                                                                ('bar',{'units':'m', 'shape':4})]: 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(some_func, compute_jacvec_product=jac_vec_func)
```


## Implicit API Description

Implicit components must have at least an `apply_nonlinear` method to compute the residual given values 
for input variables and implicit output variables (a.k.a state variables). 
From the perspective of the residual computation, both input *variables* and implicit output *variables* 
are effectively input *arguments*. 
This creates a slight API challenge, because it is ambiguous which arguments correspond to input or 
output variables. 

For explicit components, output variable names were inferred from the function source or given as part 
of the metadata in the function return annotation. That approach is also used for implicit components 
with one slight change to accommodate the output-variable function arguments. Output names must still 
be given in the return metadata, but they must name-match one of the function arguments. 

```python

def implicit_resid(x, y) -> [('y', None),]:
    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(implicit_resid)    
```


A `solve_nonlinear` method can also be specified: 

```python

@om.func_meta(out_names=['R_x', 'R_y'])
def some_implict_solve(x, y)
    # code for solve here...

def implicit_resid(x, y) -> [('y',{})]:
    R_x = x + np.sin(x+y)
    R_y = y - tan(y)**x
    return R_x, R_y

comp = om.ImplicitFuncComp(implicit_resid, solve_nonlinear=some_implicit_solve)
```

### Providing a `linearize` and/or `apply_linear` for implicit functions

The derivative APIs look very similar to the ones for those of the explicit functions, but with 
different method names to match the OpenMDAO implicit API. 
Implicit components use `linearize` and `apply_linear` methods (instead of the analogous 
`compute_partials` and `compute_jacvec_product` methods). 

```python

def deriv_implicit_resid(x, y, J): 
    ... 

@om.func_meta(default_units=None)
def implicit_resid(x, y)->[('y',{}), 
                                ('linearize', deriv_implicit_resid)]:
    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(implicit_resid)    
```

## Helper decorators

Though the annotation API is designed to be usable without any OpenMDAO dependency, the dictionary 
and list based syntax may be somewhat cumbersome. 
OpenMDAO can provide some decorators to make the syntax slightly cleaner. 

One example is the `func_meta` decorator already described. 
Two more decorators, `in_var_meta` and `out_var_meta`, will be provided to specify metadata for individual variables. 
These decorators can be stacked to fully define the component and variable metadata.

```python

def deriv_implicit_resid(x, y, J): 
    ... 

@om.in_var_meta('x', units=None, shape=1)
@om.out_var_meta('y', units=None, shape=1)
@om.func_meta(linearize=deriv_implicit_resid)
def implicit_resid(x, y):
    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(implicit_resid)    
```

## For those wanting to use this API outside of OpenMDAO

This section will describe the internal data layout that OpenMDAO expects to find within the
function `__annotations__` dict, so that developers outside of the OpenMDAO ecosystem could
potentially use the function in other ways while still keeping it compatible with OpenMDAO.

Here is an example annotated function:

```python
@om.declare_partials(of='*', wrt='*', method='fd')
@om.declare_coloring(wrt='*', method='cs')
@om.func_meta(default_units='ft')
def func(x:{'shape':4}, y:{'shape':4}, z=3) -> [('foo':{'shape':4}), ('bar',{'shape':4})]: 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

Here is what the resulting `__annotations__` dict looks like for the function above:

```python

__annotations__ = {
    'x': {'shape': 4},
    'y': {'shape': 4},
    'return': [('foo', {'shape': 4}), ('bar', {'shape': 4})],
    ':meta' : {
        'func_meta': [{'default_units': 'ft'}],
        'declare_partials': [{'of':'*', 'wrt':'*', 'method':'fd'}],
        'declare_coloring': [{'wrt':'*', 'method':'cs'}],
    }
}
```

This is just the standard `__annotations__` dict with one additional top level sub-dict named 
`:meta` that contains metadata associated with the function itself rather than individual
input variables or return values.  Each entry in `:meta` maps to a list of keyword argument dicts.
The lists contain one entry corresponding to the `**kwargs` passed into each call of the respective 
decorator in top to bottom order.
