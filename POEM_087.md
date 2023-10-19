POEM ID: 087  
Title: Expand functionality of dynamic shaping.  
authors: naylor-b (Bret Naylor)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#3000](https://github.com/OpenMDAO/OpenMDAO/pull/3000)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

Currently, the shape of a dynamically shaped variable can be determined either by the shape of
the variable it connects to, via 'shape_by_conn', or by the shape of a variable residing in the
same component, via 'copy_shape'.  Both cases only work if the desired shape happens to be the
same as the shape of the connected or named variable.

In the case of 'copy_shape' there are situations where the desired shape of an output will not
be the same as the shape of a single input but will instead be some function of the shapes of 
one or more of the component's input variables.


## Proposed solution

Since `copy_shape` doesn't properly describe the process of computing the shape based on the
shapes of other variables, a new argument called `compute_shape` will be added to `add_output` and
`add_input`. The value of `compute_shape` will be a function taking a single argument of the form 
`{'var1': shape1, 'var2': shape2, ...}`.  The argument will be populated with shapes of
all input variables in the component.  This will allow the final shape to be computed based on the
shapes of multiple variables if necessary.


## Example

A component has two dynamically shaped input matrices, 'M1' and 'M2', and an output matrix 'M3'
that is the result of the matrix multiplication M1 @ M2.  If 'M1' is shape (m, n) and 'M2' is
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
self.add_output('M3', compute_shape=shapefunc)
```

or

```
self.add_output('M3', compute_shape=lambda shapes: (shapes['M1'][0], shapes['M2'][1]))
```
