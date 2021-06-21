POEM ID:  050  
Title:  Modifications to relative step sizing in finite difference  
authors: [kenneth-t-moore]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated



Motivation
----------

When a user selects 'rel' for the `step_calc` when performing a finite difference approximation, the
stepsize for a scalar variable is computed by taking the given `step` and multiplying it by the
magnitude of the variable's current value.  If that variable is a vector, the stepsize is multiplied
by the `norm` of the entire vector. This can lead to unintuitive performance, because the norm
value is a function of the vector size. This can be verified by computing the norm of a large vector
of ones and comparing to the scalar value.  Taking the norm is not the proper way to compute a
relative stepsize.  An alternative is needed that also addresses these issues:

1. The requested step direction must be preserved independent of the sign of the local value.

2. The computed step should never be zero.


Description
-----------

This POEM proposes two new ways to compute the relative step.


Use average absolute vector value instead of the norm.
======================================================

Compute the step as:

```
    rel_step = step * np.sum(np.abs(x)) / n
```

This fixes the bug that caused the relative step to be larger than expected for wide vectors. The
absolute value ensures that we won't be taking a forward step when we request backward.


Allow the user to specify a relative step for every element in the vector.
==========================================================================

This gives the user finer control over the approximation. For `declare_partials`, the simplest API
would be to allow the user to pass a list (or tuple) with the same length as the input whose
derivatives are being approximated. Here is a simple example for a 3-wide input 'x':

```
   self.declare_partials(of='*', wrt='x', method='fd',
                         step=[1e-7, 1e-5, 1e-6], form='forward', step_calc='rel')
```

The key difference here is that relative step_size is computed individually for each vector element:
```
    rel_step_j = step_j * np.abs(x_j)
```

This API might be able to be expanded to allow specification of other aspects of the approximation:

```
   self.declare_partials(of='*', wrt='x', method='fd',
                         step=[1e-7, 1e-5, 1e-6],
                         form=['forward', 'forward', 'central'], step_calc='rel')
   self.declare_partials(of='*', wrt='x', method='fd',
                         step=[1e-7, 1e-5, 1e-6],
                         form=['forward', 'forward', 'central'],
                         step_calc=['rel', 'abs', 'rel'])
```
Note that element-wise specification of method ('fd' or 'cs') will not be possible.

All API changes would also be applied to `set_check_partial_options` as well.

The largest change would be in `approx_totals`, which currently doesn't allow settings to be
specified on a per-variable basis. A new interface would have to look like this:
```
    # In first call, we specify 'fd' and set defaults.
    model.approx_totals(method='fd', step=1e-7, form='central', step_calc='rel')

    # In subsequent calls, we set values for individual 'wrt' inputs.
    # These take precedence over defaults.
    model.approx_totals(of='sub1.comp1.y', wrt=sub1.comp1.x',
                        step=[1e-7, 1e-5, 1e-6])
```

There is a risk that implementing some or all of this API will introduce code complications that
outweigh the benefit of the feature, but that may not be understood until implementation.


Allow Both
==========

The proposed API allows both methods to exist. If the user doesn't specify element-wise steps, the
relative step can be computed from the average absolute value.

Care should be taken to make sure that zero-magnitude cases are handled by taking a small step.
