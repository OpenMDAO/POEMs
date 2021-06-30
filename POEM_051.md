POEM ID: 039  
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
One key aspect of this API is that the return annotation must provide the names of the output variables. 
While the names of the inputs are guaranteed to be able to be introspected from the function definition, the same is not true for return values. 
Consider a function like this: 

```python
def ambiguous_return_func(x,y,z):
    return 3*x, 2*y+Z

```
There is no way to infer output names from that because the computation doesn't declaring intermediate variables with names that could be parsed using the abstract syntax tree. 
So part of the information in the annotations must contain names for the output values. 

There is a simple case where all the the metadata for every input and output variable is the same (i.e. same size, units, value). 
In these cases, we can offer a more compact syntax with a function decorator: 

```python
@OMmeta(units'm', shape=4, out_names=('foo', 'bar', 'baz'))
def uniform_meta_func(x, y, z): 

    foo = x+y+z
    bar = 2*x+y
    baz = 42*foo
    return foo, bar, baz
```

### Naming I/O with invalid variable names

OpenMDAO keeps track of model variable names using strings, which gives a lot more flexibility. 
Users can include special characters such as ":" or "-" that are invalid to include in variable names. 
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




