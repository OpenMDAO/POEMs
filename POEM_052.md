POEM ID: 052  
Title:  Function based component definition for OpenMDAO  
authors: [justinsgray, Ben Margolis, Kenny Lyons]  
Competing POEMs: [056](https://github.com/OpenMDAO/POEMs/pull/121)  
Related POEMs: 039   
Associated implementation PR:  

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated

Rejected in favor of [POEM 056](https://github.com/OpenMDAO/POEMs/blob/master/POEM_056.md)

## Motivation

Define an OpenMDAO component, including all I/O with metadata, the compute method, and potentially derivatives using a purely function based syntax. 

## Explicit API Description

A purely function based syntax for component definition has several nice properties. 
It offers a fairly compact syntax, especially in cases where there is uniform metadata all I/O in the component. 
It also provides an interface that is much more compatible with algorithmic differentiation than the traditional dictionary-like arguments to the `compute` method of the standard OpenMDAO API. 

The proposed functional component API in this POEM was inspired by the function registration API in POEM_039, 
but seeks to extend that concept much further to allow full component definitions (i.e. more than exec-comps) using nothing more than a python function definition. 
Since Python 3.0, the language has supported function annotations which can be used to provide any and dictionaries of metadata that a special component can interrogate and then wrap in the normal OpenMDAO API. 

Here is a basic example of the proposed API for a function with three inputs (`x,y,z`) and two outputs (`foo,bar`)

```python
def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> [('foo', {'units':1/m, 'shape':4}), 
                  ('bar', {'units':'m', 'shape':4})]:

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```


### No direct OpenMDAO Dependency 

The use of simple Python data structures is intentional.
It allows users to build capability that has no direct dependence on OpenMDAO. 
The annotations contain all the metadata, except for the default value which can be provided by normal python syntax for default argument values. 
An overarching goal of this API is to include all the critical data in the function annotations themselves. 
No additional data should be needed when creating a `FuncComponent` other than the function itself. 

### Why return annodations must provide output names 

While the names of the inputs are guaranteed to be able to be introspected from the function definition, the same is not true for return values. 
Consider a function like this: 

```python
def ambiguous_return_func(x,y,z):
    return 3*x, 2*y+Z

```
There is no way to infer output names from that because the computation doesn't declaring intermediate variables with names at all. 
Hence out variable names have to be given as part of the function annotation. 

### Return annotations must be either list of tuple or OrderedDict

It API provides output annotations in a strictly ordered data structure so that the metadata can be matched with the correct return value. 
So return annotations must be either a list of (<var_name>, <var_meta>) or alternatively users can provide an OrderedDict. 
```python
def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> OrderedDict(('foo', {'units':1/m, 'shape':4}), 
                             ('bar', {'units':'m', 'shape':4})):

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

Note: a standard dictionary is not allowed and will raise an error when creating the OpenMDAO component because it lacks the ordering necessary to properly resolve the outputs.
```python
def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> Dict(('foo', {'units':1/m, 'shape':4}), 
                      ('bar', {'units':'m', 'shape':4})):

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

try: 
    comp = om.ExplicitFuncComp(some_func,)
except ValueError: 
    print('Not Allowed!!!')    
```

### Shorthand for uniform metadata 
There is a simple case where all the the metadata for every input and output variable is the same (i.e. same size, units, value). 
In these cases, we can offer a more compact syntax with a function decorator: 

```python
@om.func_meta(units'm', shape=4, out_names=('foo', 'bar', 'baz'))
def uniform_meta_func(x, y, z): 

    foo = x+y+z
    bar = 2*x+y
    baz = 42*foo
    return foo, bar, baz
```

Any annotations provided in the function definition will take precedence over the ones given in the decorator

### Naming I/O with non-valid Python variable names

OpenMDAO keeps track of model variable names using strings, which gives a lot more flexibility. 
Users can include special characters (e.g. ":","-") that are invalid to include in Python variable names. 
Using the above API based on function introspection, the output names are still given as strings but the input names must use valid python variable syntax. 
Sometimes, this restriction can be limiting --- especially when you are adding a component to a larger model that has existing variable naming conventions you wish to follow. 
While you could work around the limitation using aliasing of the promoted names, 
it may be more convenient to provide a string based name for inputs as part of the annotation. 

```python
def some_func(x:{'units':'m', 'name'='flow:x'}=np.zeros(4),
              y:{'units':'m', 'name'='flow:y'}=np.ones(4),
              z:{'units':None, 'name'='flow:z'}=3) 
              -> [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4})] : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```
When `name` metadata is given, OpenMDAO will use the string provided instead of the argument name. 

### Variable sizing 

One unique aspect of OpenMDAO variable metadata syntax is that you can specify a scalar default value and a non-scalar size, 
and OpenMDAO interprets that to mean `np.ones(shape)*default_val`. 
For consistency, the functional API will respect the convention. 
If a shape is given as metadata, then the default value will be broadcast out to that shape. 

```python
def some_func(x:{'units':'m', 'shape':4}=0.,
              y:{'units':'m', 'shape':4}=1.,
              z:{'units':None}=3) 
              -> [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4})] : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```
Note: If `shape` metadata is given along with a non-scalar default value for the argument, then an error will be raised during setup by OpenMDAO. 



## Adding a FuncComponent to a model 
OpenMDAO will add a new Component to the standard library called `FuncComponent`, which will accept one or more functions as arguments and will then create the necessary component and all associated I/O

```python
def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              ->  [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4})] : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

@OMmeta(units'm', shape=4, out_names=('baz'))
def some_other_func(x, y): : 
    return x**y

comp = om.ExplicitFuncComp(some_func, some_other_func)    
```

The resulting `comp` component instance would have three inputs: `x`, `y`, `z`. 
It would have three outputs `foo`, `bar`, `baz`. 
Note that no two output names on different functions can be the same, since that would cause a name conflict in the output list. 

## Providing partial derivatives

Users should have access to the full `declare_partials` API, including specifying any details about finite difference or complex-step approximations and also use the `declare_coloring` component API. 

### Using `declare_partials` and `declare_coloring`

```python

def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> [('foo':{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4}),, 
                  ('declare_partials', [{'of':'*', 'wrt':'*', 'method':'cs'},]), 
                  ('declare_coloring', [{'wrt': '*', 'method':'cs'},])
                 ]: 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(some_func,)    
```

The dictionary keys intentionally match the existing OpenMDAO API method names. 
The use of a list of dictionaries for the `declare_partials` data is also intentional. 
The OpenMDAO API respects the partials declaration order, with later calls taking precedence over earlier ones. 
The same is true for declare coloring. 
As a shorthand, if a user is going to provide only a single dictionary they can skip the list. 

```python

def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4}), 
                  ('declare_partials', {'of':'*', 'wrt':'*', 'method':'cs'}), 
                  ('declare_coloring', {'wrt': '*', 'method':'cs'}),
                 ]: 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(some_func,)    
```

### Providing a `compute_partials` or `compute_jacvec_product`

Users can provide a secondary function that gives `compute_partials` functionality. 
For `compute_partials`, the argument structure must follow that of the primary function, with the last argument being a provided Jacobian object. 
Just like a normal OpenMDAO component, the shape of the expected derivative data is determined by the shapes of the inputs and outputs and whether or not any rows and cols are given. 

```python

def J_some_func(x, y, z, J): 

    J['foo', 'x'] = -3*np.log(z)(3*x+2*y)**2 
    J['foo', 'y'] = -2*np.log(z)(3*x+2*y)**2 
    J['foo', 'z'] = 1/(3*x+2*y) * 1/z

    J['bar', 'x'][:] = 2 # need to set all elements of array
    J['bar', 'y'][:] = 1 # need to set all elements of array

def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4}), 
                  ('declare_partials', [{'of':'foo', 'wrt':'*', 'rows':np.arange(4), 'cols':np.arange(4)}, 
                                        {'of':'bar', 'wrt':('x', 'y'), 'rows':np.arange(4), 'cols':np.arange(4)}
                                       ]),
                  ('compute_partials',J_some_func)
                 ]: 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(some_func,)    
```

Just like a normal explicit component, if you are using the matrix free API then you should not declare any partials. 
The matrix vector product method method signature will expect three additional arguments added beyond those in the nonlinear function: `d_inputs, d_outputs, mode` 

```python

def jac_vec_some_func(x, y, z, d_inputs, d_outputs, mode):
    ...  

def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> [('foo',{'units':1/m, 'shape':4}), ('bar',{'units':'m', 'shape':4}), 
                  ('compute_jacvec_product', jac_vec_some_func), 
                 ] : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = om.ExplicitFuncComp(some_func,)    
```


## Implicit API Description

Implicit components must have at least an `apply_nonlinear` method to compute the residual given values for input variables and implicit output variables (a.k.a state variables). 
From the perspective of the residual computation, both input *variables* and implicit output *variables* are effectively input *arguments*. 
This creates a slight API challenge, because it is ambiguous which arguments correspond to input or output variables. 

For explicit components, output variable names were given as part of the metadata in the function return annotation. 
That approach is also used for implicit components with one slight change to accommodate the output-variable function arguments. 
Output names must still be given in the return metadata, but they must name-match one of the function arguments. 

```python

@om.func_meta(units=None, shape=1)
def some_implicit_resid(x, y) -> [('y', None),]:

    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(some_implicit_resid,)    
```

If you want to use OpenMDAO variables names that contain characters that are non valid for arguments, then provide `name` metadata for that output. 

```python

@om.func_meta(units=None, shape=1)
def some_implicit_resid(x, y)->[('y',{'name':'foo:y'})]:

    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(some_implicit_resid,)    
```


A `solve_nonlinear` method can also be specified as part of the metadata: 

```python
@om.func_meta(units=None, shape=1, out_names=['R_x', 'R_y'])

def some_implict_solve(x,y)

def some_implicit_resid(x, y)-> >[('y',{'name':'foo:y'}), 
                                  ('solve_nonlinear',some_implict_solve)
                                 ]:

    R_x = x + np.sin(x+y)
    R_y = y - tan(y)**x
    return R_x, R_y

comp = om.ImplicitFuncComp(some_implicit_resid,)    
```

### Providing a `linearize` and/or `apply_linear` for implicit functions

The derivative APIs look very similar to the ones for those of the explicit functions, but with different method names to match the OpenMDAO implicit API. 
Implicit components use `linearize` and `apply_linear` methods (instead of the analogous `compute_partials` and `compute_jacvec_product` methods). 

```python

def deriv_implicit_resid(x, y, J): 
    ... 

@om.func_meta(units=None, shape=1)
def some_implicit_resid(x, y)->[('y',{'name':'foo:y'}), 
                                ('linearize', deriv_implicit_resid)]:

    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(some_implicit_resid,)    
```

## Helper decorators

Though the annotation API is designed to be usable without any OpenMDAO dependency, the dictionary and list based syntax may be somewhat cumbersome. 
OpenMDAO can provide some decorators to make the syntax slightly cleaner. 

One example is the `func_meta` decorator already described. 
Two more decorators, `in_var_meta` and `out_var_meta`, will be provided to specify metadata for individual variables. 
These decorators can be stacked to fully defined the component and variable metadata.

```python

def deriv_implicit_resid(x, y, J): 
    ... 

@om.in_var_meta('x', units=None, shape=1)
@om.out_var_meta('y', units=None, shape=1, name='foo:y')
@om.func_meta(linearize=deriv_implicit_resid)
def some_implicit_resid(x, y):

    R_y = y - tan(y**x)
    return R_y

comp = om.ImplicitFuncComp(some_implicit_resid,)    
```
