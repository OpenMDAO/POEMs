POEM ID: 056  
Title:  Function based API usable by OpenMDAO and others  
authors: [Bret Naylor]  
Competing POEMs: 052    
Related POEMs: 039   
Associated implementation PR: [#2281](https://github.com/OpenMDAO/OpenMDAO/pull/2281)

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


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

This API consists primarily of methods on the OMWrappedFunc class, which wraps a plain python 
function and stores metadata needed by openmdao along with that function.

To obtain a wrapped function requires a call to the `wrap` function.

```python
def func(a, b, c):
    d = a * b + c
    return d

f = omf.wrap(func)
```

The wrapped function has a number of methods for setting and retrieving metadata. The setting
methods all return the function wrapper instance so they can be stacked together to allow a 
somewhat more concise syntax if desired.  For example:

```python
f = omf.wrap(func).defaults(shape=5).add_input('x', units='m').add_output('y', units='ft')
```

The stacked methods can also be lined up vertically, but only if the entire expression is enclosed in
parentheses.  For example:

```python
f = (omf.wrap(func)
        .defaults(shape=5)
        .add_input('x', units='m')
        .add_output('y', units='ft'))
```

If stacking isn't desired, the methods can just be called in the usual way:

```python
f = omf.wrap(func)
f.defaults(shape=5)
f.add_input('x', units='m')
f.add_output('y', units='ft')
```

## Variable metadata

### Setting the metadata for a single variable

OpenMDAO needs to know a variable's shape, initial value, and optionally other things like units.  
This information can be specified using the `add_input` and `add_output` methods.  For example:

```python
def func(x):
    y = x.dot(np.random.random(2)).
    return y

f = (omf.wrap(func)
        .add_input('x', shape=(2,2))
        .add_output('y', shape=2))
```

### Setting metadata for option variables

A function may have additional non-float or not float ndarray arguments that, at least in the
OpenMDAO context, will be treated as component options that don't change during a given model
execution.  These can be specified using the `declare_option` method.  For example:

```python

def func(x, opt):
    if opt == 1:
        y = x.dot(np.random.random(2))
    elif opt == 2:
        y = x[:, 1] * 2.
    elif opt == 3:
        y = x[1, :] * 3.
    return y

f = (omf.wrap(func)
        .add_input('x', shape=(2,2))
        .declare_option('opt', values=[1, 2, 3])
        .add_output('y', shape=2))
```

### Setting metadata for multiple variables

Using the `add_inputs` and `add_outputs` methods you can specify metadata for multiple variables
in the same call.  For example:

```python
def func(a):
    return a.dot(b), a[:,0] * b * b

f = (omf.wrap(func)
        .add_inputs(a={'shape': (2,2), 'units': 'm'}, b={'shape': 2, 'units': 'm'})
        .add_outputs(x={'shape': 2, 'units': 'm**2'}, y={'shape': 2, 'units': 'm**3'}))
```

It's also possible, depending on the contents of the function, that the output shapes could be 
determined automatically using the `jax` package.  This functionality could be implemented in 
such a way that `jax` would not be a hard dependency but would only be used if found.  This
could remove some boilerplate from the function metadata specification, but would have the 
unfortunate side effect of making that particular function definition dependent on `jax`, i.e. if 
someone with `jax` created the function as part of a library and that library was used by someone 
else without `jax` then the function definition would raise an exception because the output shape(s) 
would be unknown.  This is not an issue if `declare_partials` (see below) specifies that `jax` be 
used as the method to compute partial derivatives because in that case, there will already be a `jax` 
dependency.


### Getting the metadata

Variable metadata is retrieved from the callable object by passing that object to the `get_input_meta`
and `get_output_meta` methods. Each function returns an iterator over (name, metadata_dict) tuples, 
one for each input or output variable respectively.  For example, the following code snippet will
print the name and shape of each output variable (assuming f is a wrapped function).

```python
for name, meta in f.get_output_meta():
    print(name, meta['shape'])
```

Note that in addition to user supplied metadata, metadata for each added output will include a
'deps' entry which contains a set of names of inputs that that output depends on.  This does
not include any sparsity information if the input and/or output are array variables.  It only 
shows whether a given output depends in any way upon a particular input variable.

## Setting function default metadata

Some metadata will be the same for all, or at least most of the variables within a given function,
so we want to be able to specify those defaults easily without too much boilerplate.  That's the
purpose of the `defaults` method.  For example:

```python
def func(a, b, c):
    d = a * b * c
    return d

f = omf.wrap(func).defaults(shape=4, units='m')
```

Any metadata that is specific to a particular variable will override any defaults specified in
`defaults`. For example:

```python
def func(a, b, c=np.ones(3)):  # shape of c is 3 which overrides the `defaults` shape
    d = a * b
    e = c * 1.5
    return d, e

f = omf.wrap(func).defaults(shape=4, units='m')
```


### Assumed default values

In order to stay consistent with OpenMDAO's default value policy, we'll assume the same default
behavior for functions, so if no shape or default value is supplied for a function variable, we'll
assume that is has the value 1.0.  If the `shape` is provided and either the default value is
not provided or is provided as a scalar value, then the assumed default value will be
`np.ones(shape) * scalar_value`, where `scalar_value` is 1.0 if not specified.
If `shape` is provided along with a non-scalar default value that has a different shape, then
an exception will be raised.


## Variable names

### Setting variable names

We don't need to set input names because the function can always be inspected for those, but
we do need to associate output names with function return values. Those return values, if they are 
simple variables, for example, `return x, y`, will give us the output variable names we need.  
But in those cases where the function returns expressions rather than simple variables, we need 
another way to specify what the names of those output variables should be.  The `output_names` 
method provides a concise way to do this, for example:


```python
def func(a, b, c):
    return a * b * c, a * b -c  # two return values that don't have simple names

f = omf.wrap(func).output_names('d', 'e')  # name of return values are 'd' and 'e'
```

If we don't want to bother with a separate method for output names, we could instead use the
`add_outputs` method mentioned earlier, for example:

```python
def func(a, b, c):
    return a * b * c, a * b -c  # two return values that don't have simple names

# names of return values are 'd' and 'e' and they have no other metadata
f = omf.wrap(func).add_outputs(d={}, e={})
```

As mentioned above, if the function's return values are simple variable names, we don't need to
call `output_names` because we can determine the names from inspecting the function, e.g., 


```python
def func(a, b, c):
    d = a * b * c
    e = a * b -c
    return d, e  # we know from inspection that the output names are 'd' and 'e'
```

Note that in the function above, we didn't have to wrap it at all.  This is possible because we can 
inspect the source code to determine the output names and we assume the default value of all inputs
and outputs is 1.0.  If any inputs or outputs of a function have any non-default metadata, e.g.,
val, units, shape, etc., then that function would have to be wrapped and those metadata values
would have to be specified.

If neither `output_names` nor `add_outputs` is specified and the output names cannot be 
determined by inspection of the return values, then they must be specified using `add_output` calls, 
and the order of those `add_output` calls determines how those names map to the return value positions.  For example:

```python
def func(x):
    return x.dot(np.random.random(2))., x*1.5  # 2 return values and we can't infer the names

f = (omf.wrap(func)
        .add_input('x', shape=(2,2))
        .add_output('y', shape=2)       # 'y' is the name of the first return value
        .add_output('z', shape=(2,2)))  # 'z' is the name of the second return value
```

In the example above, the output names would be assumed to be `['y', 'z']`.


### Getting variable names

Lists of input names and output names can be retrieved by calling `get_input_names` and 
`get_output_names` respectively, e.g., 

```python

invar_names = f.get_input_names()
outvar_names = f.get_output_names()

```

## Partial derivatives

### Setting partial derivative information

Metadata that will help OpenMDAO or potentially other libraries to compute partial derivatives
for the function can be defined using the `declare_partials` and `declare_coloring` methods.
For example:

```python

def func(x, y, z=3): 
    foo = np.log(z)/(3*x+2*y)
    bar = 2*x+y
    return foo, bar

f = (omf.wrap(func)
        .declare_partials(of='*', wrt='*', method='cs')
        .declare_coloring(wrt='*', method='cs')
        .defaults(shape=4))
```

The args for the `declare_partials` and `declare_coloring` methods match those
of the  `declare_partials` and `declare_coloring` methods of an OpenMDAO component.  Multiple calls
can be made to `declare_partials` to set up different partials, but `declare_coloring` may only
be called once.

Note that for a regular OpenMDAO component, the `method` argument can currently only have values of
'fd' or 'cs'. This function based API allows one additional allowed value, 'jax', which specifies that 
the 'jax' library be used to compute derivatives using AD.  In the future it's possible that 'jax'
will also be added as an allowed value for `method` in regular OpeMDAO components as well.


### Getting partial derivative information

The args passed to the `declare_partials` and `declare_coloring` methods can be retrieved 
using the `get_declare_partials` and `get_declare_coloring` methods respectively.  Each of these
returns a list where each entry is the keyword args dict from each call, in the order that they
where called.

```python

dec_partials_calls = f.get_declare_partials()  # gives list of args dicts for multiple calls
dec_coloring_args = f.get_declare_coloring()   # gives args dict for a single call

```
