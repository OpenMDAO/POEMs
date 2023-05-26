POEM ID: 087  
Title: Expand functionality of dynamic shaping.  
authors: @naylor-b  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: 

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

Currently, the shape of a dynamically shaped variable can be determined either by the shape of
the variable it connects to, via 'shape_by_conn', or by the shape of a variable residing in the
same component, via 'copy_shape'.  Both cases only work if the desired shape happens to be the
same as the shape of the connected or named variable.

In the case of 'copy_shape' there are situations where the desired shape of an output will not
be the same as the shape of a single input but will instead be some function of the shapes of 
one or more of the component's input variables.


## Proposed solutions

Altering the allowed values of `copy_shape` to include a tuple of the form 
`(var_names, func)`, where:

- `var_names` is a list of variable names
- func is a function taking a dict arg of the form `{'var1': shape1, 'var2': shape2, ...}` 
and returning the desired shape


would allow the desired shape to be computed based on the shapes of multiple variables from 
the same component if necessary.


In the example below, the value of `copy_shape` is modified as to be a tuple as shown above, but
this brings up another issue.  This new operation is not simply copying the shape of a specified
variable, so the name `copy_shape` isn't really accurate any more.  There are three ways to address
this.

1) We just ignore it and allow `copy_shape` to have either its typical string value or the new tuple
value
2) We rename `copy_shape` to something else like `compute_shape` and deprecate `copy_shape`.
3) We leave `copy_shape` as is and add a new metadata attribute called `compute_shape` that is
required to have a tuple value as explained above.


## Example

A component has two dynamically shaped input matrices, 'M1' and 'M2', and an output matrix 'M3'
that is the result of the matrix multiplication M1 * M2.  If 'M1' is shape (m, n) and 'M2' is
shape (n, p), then the desired shape of 'M3' is (m, p).  This can be computed using the function

```
def shapefunc(shapes):
    return (shapes['M1'][0], shapes['M2'][1])
```

or 

```
lambda shapes: (shapes['M1'][0], shapes['M2'][1])
```


So, when adding output 'M3' to its parent component, the add_output call would look something
like this:

```
self.add_output('M3', copy_shape=(['M1', 'M2'], shapefunc))
```

or

```
self.add_output('M3', copy_shape=(['M1', 'M2'], lambda shapes: (shapes['M1'][0], shapes['M2'][1])))
```