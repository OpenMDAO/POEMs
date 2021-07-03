POEM ID: 052
Title:  Function based component definition for OpenMDAO
authors: [justinsgray, Ben Margolis, Kenny Lyons]  
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

Define an OpenMDAO component, including all I/O with metadata, the compute method, and potentially derivatives using a purely function based syntax. 

## API Description

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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}} : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar
```

The use of simple dictionaries is intentional, because it allows users to build capability that has no direct dependence on OpenMDAO. 
The annotations contain all the metadata, except for the default value which can be provided by normal python syntax for default argument values. 
An overarching goal of this API is to include all the critical data in the function annotations themselves. 
No additional data should be needed when creating a `FuncComponent` other than the function itself. 

One key aspect of this API is that the return annotation must provide the names of the output variables. 
While the names of the inputs are guaranteed to be able to be introspected from the function definition, the same is not true for return values. 
Consider a function like this: 

```python
def ambiguous_return_func(x,y,z):
    return 3*x, 2*y+Z

```
There is no way to infer output names from that because the computation doesn't declaring intermediate variables with names that could be parsed using the abstract syntax tree. 
So output data needs to be given as a nested dictionary annotation on the function return. 


### Shorthand for uniform metadata 
There is a simple case where all the the metadata for every input and output variable is the same (i.e. same size, units, value). 
In these cases, we can offer a more compact syntax with a function decorator: 

```python
@om.io_meta(units'm', shape=4, out_names=('foo', 'bar', 'baz'))
def uniform_meta_func(x, y, z): 

    foo = x+y+z
    bar = 2*x+y
    baz = 42*foo
    return foo, bar, baz
```

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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}} : 

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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}} : 

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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}} : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

@OMmeta(units'm', shape=4, out_names=('baz'))
def some_other_func(x, y): : 
    return x**y

comp = FuncComp(some_func, some_other_func)    
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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}, 
                  'declare_partials': [{'of':'*', 'wrt':'*', 'method':'cs'},], 
                  'declare_coloring': [{'wrt': '*', 'method':'cs'},]
                 } : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = FuncComp(some_func,)    
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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}, 
                  'declare_partials': {'of':'*', 'wrt':'*', 'method':'cs'}, 
                  'declare_coloring': {'wrt': '*', 'method':'cs'}
                 } : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = FuncComp(some_func,)    
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
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}, 
                  'declare_partials': [{'of':'foo', 'wrt':'*', 'rows':np.arange(4), 'cols':np.arange(4)}, 
                                       {'of':'bar', 'wrt':('x', 'y'), 'rows':np.arange(4), 'cols':np.arange(4)}
                                      ], 
                   'compute_partials': J_some_func,
                 } : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = FuncComp(some_func,)    
```

Just like a normal component, if you are using the matrix free API then you don't want to declare any partials. 
The matrix free API will expect three additional arguments added beyond those in the nonlinear function: `d_inputs, d_outputs, mode` 

```python

def jac_vec_some_func(x, y, z, d_inputs, d_outputs, mode):
    ...  

def some_func(x:{'units':'m'}=np.zeros(4),
              y:{'units':'m'}=np.ones(4),
              z:{'units':None}=3) 
              -> {'foo':{'units':1/m, 'shape':4}, 'bar':{'units':'m', 'shape':4}, 
                  'compute_jacvec_product': jac_vec_some_func, 
                 } : 

    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

comp = FuncComp(some_func,)    
```
