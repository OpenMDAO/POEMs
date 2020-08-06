POEM ID: 018         
Title: indices and src_indices can contain slices  
authors: @Kenneth-T-Moore         
Competing POEMs: [N/A]   
Related POEMs: [N/A]  
Associated implementation PR:                                                                    

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

OpenMDAO, like other Python-based tools, has much-improved performance when using vectorized calculations.
We really make use of this in Dymos, where a calculation on a scalar is performed simultaneously at `n`
points (nodes).  A scalar variable is stored in OpenMDAO with shape `(n,)`.

If we want to model a 3-vector at n points, then the shape is `(n, 3)`.  A 3x3 matrix would be `(n, 3, 3)`, etc.

Consider having a 3-vector representing position, and another calculation which only relies on the 3rd index (3rd column) of that vector.
In straight up numpy, we would do something like:

```
input[:] = output[:, 2]
```

In OpenMDAO, `src_indices` is currentlty required to be a sequence of ints, and building it for a case like this is a non-trivial effort.
Unfortunately, we can't pass `[:, 2]` as src_indices because it isn't legal Python.
But Python does have a `slice` object that allows us to do this.

```
g.connect('x', 'y', src_indices=(slice(None), 2))
```

or alternatively, using `numpy.s_`:

```
import numpy as np
g.connect('x', 'y', src_indices=np.s_[:, 2])
```

This is also useful in OpenMDAO's `set_val` method on Problem.
If we want to assign a column of an `(n, 3)` variable, its much easier to use the dictionary access, but that lacks unit conversion.

```
p['pos'][:, 2] = 5.0

p.set_val('pos', 5.0, indices=???)
```

Under the new notation, one could do

```
p.set_val('pos', 5.0, indices=(slice(None), 2))
```

or using numpy:

```
import numpy as np
p.set_val('pos', 5.0, indices=np.s_[:, 2)
```

Description
-----------

Those functions and methods which have arguments for `indices` or `src_indices` will allow them to be tuples which contain integers or slice objects.
At setup time, these slice objects can be converted to an expanded list of numeric indices.


