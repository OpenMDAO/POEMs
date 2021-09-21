POEM ID: 056  
Title:  Function based API usable by OpenMDAO and others  
authors: [Bret Naylor]  
Competing POEMs: 052    
Related POEMs: 039   
Associated implementation PR:  

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


First a note about competing POEM 52.  This POEM is more limited in scope than POEM 52 and 
focuses only on the API for associating metadata with and retrieving metadata from a function
object.  POEM 52 also deals with the OpenMDAO function component(s) that will use the API it defines.
This POEM does not describe those components in any detail and will defer that discussion to a later 
POEM.


## Motivation

Define an API for attaching metadata to and retrieving metadata from a function object.  This API
will enable a user to attach metadata to a function object sufficient for OpenMDAO to create a 
fully operational Component, including input and output variable names, shapes and units as well
as partial derivative and coloring information.  The body of the function will act as the 
component's `compute` method.

Depending upon the importance of eliminating any dependence on OpenMDAO, this API could either be
released as a standalone distribution called, for example, `openmdao_func_api`, or as just a
sub-package within the openmdao distribution, e.g., `openmdao.func_api`.

For the rest of this document, assume that we've imported this package as either

```python
import openmdao_func_api.api as omf
```

or

```python
import openmdao.func_api as omf
```

A two-way API as described above, where API functions are used to both attach and retrieve data,
allows the underlying data layout and location to be hidden and potentially updated later without 
negatively impacting users of the API.


## Variable metadata

### Setting the metadata for a single variable

OpenMDAO needs to know a variable's shape, initial value, and optionally other things like units.  
This information can be specified using the `add_input` and `add_output` decorators.  For example:

```python
@omf.add_input('x', shape=(2,2))
@omf.add_output('y', shape=2)
def func(x):
    y = x.dot(np.random.random(2)).
    return y
```

### Setting metadata for option variables

A function may have additional non-float or not float ndarray arguments that, at least in the
OpenMDAO context, will be treated as component options that don't change during a given model
execution.  These can be specified using the `declare_option` decorator.  For example:

```python

@omf.add_input('x', shape=(2,2))
@omf.declare_option('opt', values=[1, 2, 3])
@omf.add_output('y', shape=2)
def func(x, opt):
    if opt == 1:
        y = x.dot(np.random.random(2))
    elif opt == 2:
        y = x[:, 1] * 2.
    elif opt == 3:
        y = x[1, :] * 3.
    return y

```

### Setting metadata for multiple variables

Using the `add_inputs` and `add_outputs` decorators you can specify metadata for multiple variables
in the same decorator.  For example:

```python
@omf.add_inputs(a={'shape': (2,2), 'units': 'm'}, b={'shape': 2, 'units': 'm'})
@omf.add_outputs(x={'shape': 2, 'units': 'm**2'}, y={'shape': 2, 'units': 'm**3'})
def func(a):
    return a.dot(b), a[:,0] * b * b

```

It's also possible, depending on the contents of the function, that the output shapes could be 
determined automatically using the `jax` package.  This functionality could be implemented in 
such a way that `jax` would not be a hard dependency but would only be used if found.  This
could remove some boilerplate from the function decoration, but would have the unfortunate side
effect of making that particular function definition dependent on `jax`, i.e. if someone with
`jax` created the function as part of a library and that library was used by someone else without
`jax` then the function definition would raise an exception because the output shape(s) would be
unknown.  This is not an issue if the function is decorated with `declare_partials` (see below)
specifying that `jax` be used as the method to compute partial derivatives because in that case,
there will already be a `jax` dependency.


### Getting the metadata

Variable metadata is retrieved from the callable object by passing that object to the `get_input_meta`
and `get_output_meta` functions. Each function returns a list of (name, metadata_dict) tuples, one for
each input or output variable respectively.  For example, the following code snippet will
print the name and shape of each output variable.

```python
for name, meta in omf.get_output_meta(func):
    print(name, meta['shape'])
```

## Setting function default metadata

Some metadata will be the same for all, or at least most of the variables within a given function,
so we want to be able to specify those defaults easily without too much boilerplate.  That's the
purpose of the `defaults` decorator.  For example:

```python
@omf.defaults(shape=4, units='m')
def func(a, b, c):
    d = a * b * c
    return d
```

Any metadata that is specific to a particular variable will override any defaults specified in
`defaults`. For example:

```python
@omf.defaults(shape=4, units='m')
def func(a, b, c=np.ones(3)):  # shape of c is 3 so just override default shape
    d = a * b
    e = c * 1.5
    return d, e
```

### Getting the function default metadata

Currently there doesn't seem to be a need to add this, as the defaults are automatically applied
to the variable metadata, but a function to do this could easily be added later if needed.


### Assumed default values

In order to stay consistent with OpenMDAO's default value policy, we'll assume the same default
behavior for functions, so if no shape or default value is supplied for a function variable, we'll
assume that is has the value 1.0.  If the `shape` is provided and either the default value is
not provided or is provided as a scalar value, then the assumed default value will be
`np.ones(shape) * scalar_default_value`, where `scalar_default_value` is 1.0 if not specified.
If `shape` is provided along with a non-scalar default value that has a different shape, then
an exception will be raised.


## Setting non-default function metadata

The `metadata` decorator can be used to specify metadata that is intended to apply to the function 
as a whole.  It's similar to `defaults` in that it describes metadata for the whole function, but unlike
`defaults`, a conflicting metadata value will raise an exception.  One possible source of conflict 
is if a function default argument differs in shape from a shape specified in `metadata`. For example:


```python
@omf.metadata(shape=4, units='m')  # name of return value is 'd'
def func(a, b, c=np.ones(3)):  # shape of c is 3 so raise an exception
    d = a * b
    e = c * 1.5
    return d, e
```


## Variable names

### Setting variable names

We don't need to set input names because the function can always be inspected for those, but
we also need to associate output names with function return values. Those return values, if they are 
simple variables, for example, `return x, y`, will give us the output variable names we need.  
But in those cases where the function returns expressions rather than simple variables, we need 
another way to specify what the names of those output variables should be.  The `output_names` 
decorator provides a concise way to do this, for example:


```python
@omf.output_names('d', 'e')  # name of return values are 'd' and 'e'
def func(a, b, c):
    return a * b * c, a * b -c
```

If we don't want to bother with a separate decorator for output names, we could instead use the
`add_outputs` decorator mentioned earlier, for example:

```python
@omf.add_outputs(d={}, e={})  # name of return values are 'd' and 'e' and they have no other metadata
def func(a, b, c):
    return a * b * c, a * b -c
```

As mentioned above, if the function's return values are simple variable names, we don't need to
call `output_names` because we can determine the names from inspecting the function, e.g., 


```python
def func(a, b, c):
    d = a * b * c
    e = a * b -c
    return d, e  # output names are 'd' and 'e'. no call to output_names needed
```

Note that if neither `output_names` nor `add_outputs` is specified and the output names cannot be 
determined by inspection of the return values, then they must be specified using `add_output` calls, 
and the order (top to bottom) of those `add_output` calls determines how those names map to the return value positions.  For example:

```python
@omf.add_input('x', shape=(2,2))
@omf.add_output('y', shape=2)
@omf.add_output('z', shape=(2,2))
def func(x):
    return x.dot(np.random.random(2))., x*1.5
```

In the example above, the output names would be assumed to be `['y', 'z']`.


### Getting variable names

Lists of input names and output names can be retrieved by calling `get_in_names` and `get_output_names`
respectively, e.g., 

```python

invar_names = omf.get_in_names(func)
outvar_names = omf.get_output_names(func)

```

## Partial derivatives

### Setting partial derivative information

Metadata that will help OpenMDAO or potentially other libraries to compute partial derivatives
for the function can be defined using the `declare_partials` and `declare_coloring` decorators.
For example:

```python

@omf.declare_partials(of='*', wrt='*', method='cs')
@omf.declare_coloring(wrt='*', method='cs')
@omf.defaults(shape=4)
def func(x, y, z=3): 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

```

The args for the `declare_partials` and `declare_coloring` decorators match those
of the  `declare_partials` and `declare_coloring` methods of an OpenMDAO component.  Multiple calls
can be made to either decorator to set up different partials/colorings.  The partials will be
ordered top to bottom, just as they would be if the corresponding methods were called on a
component.

Note that for a regular OpenMDAO component, the `method` argument can have values of 'fd' or 'cs'.
This function based API allows one additional allowed value, 'jax', which specifies that the 
'jax' library be used to compute derivatives using AD.


### Getting partial derivative information

The args passed to the `declare_partials` and `declare_coloring` decorators can be retrieved 
using the `get_declare_partials` and `get_declare_coloring` calls respectively.  Each of these
returns a list where each entry is the keyword args dict from each call, in top to bottom order.

```python

dec_partials_calls = omf.get_declare_partials(func)
dec_coloring_calls = omf.get_declare_coloring(func)

```

## Late calls to decorators

Arguments passed to decorators are determined at the time that the function is defined, which can
in some cases be earlier than desired.  If this is the case, keeping in mind that decorators are
just syntactic sugar for calling a normal function that takes a function as an arg and returns a
function, we could provide a function to make the decorator processing of a function less painful
if it must be done at some time other than function definition time.

```python

myfunc = omf.apply_decorators(func, 
                              omf.declare_partials(of='*', wrt='*', method='cs'),
                              omf.declare_coloring(wrt='*', method='cs'),
                              omf.defaults(shape=myshape)
                             )

```
