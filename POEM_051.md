POEM ID:  051  
Title:  Modifications to relative step sizing in finite difference  
authors: Kenneth-T-Moore (Ken Moore)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:  [PR 2209](https://github.com/OpenMDAO/OpenMDAO/pull/2209)   

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated



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


Use average absolute vector value.
==================================

Compute the step for a variable's vector as:
```
    rel_step = step * np.sum(np.abs(x)) / n
```

This fixes the bug that caused the relative step to be larger than expected for wide vectors. The
absolute value ensures that we won't be taking a forward step when we request backward.

Note, changing the default behavior for the relative step size is a disruptive change that can
affect and break existing models. To prevent that from happening, we create a new step_calc
method for enabling relative stepping with the average vector value.
```
    # Uses the vector average absolute value.
    self.declare_partials(of='*', wrt='x', method='fd', step_calc='rel_avg')
```


Use value of each element.
==========================

Compute the step for an element of a variable's vector as:
```
    rel_step_j = step_j * np.abs(x_j)
```

The key difference here is that relative step_size is computed individually for each vector element.
This is a better choice for vectors whose elements with disparate magnitude ranges. The user can
select this method by choosing 'rel_element' as the value for the step_calc argument.
```
   self.declare_partials(of='*', wrt='x', method='fd',
                         step=1e-7, form='forward', step_calc='rel_element')
```

When sizing steps individually, there is more risk of encountering an element whose value is close to
zero. In such a case, the finite difference needs to take some small step to prevent division by zero,
so a new option "minimum step" will be added.
```
   self.declare_partials(of='*', wrt='x', method='fd',
                         step=1e-7, form='forward', step_calc='rel_element',
                         minimum_step=1e-9)
```

Deprecation of the current method
=================================

To preserve legacy model performance, the old method in 'rel' can be kept available by selecting
'rel_legacy' for the step_calc.

To minimize impact on existing models, the current behavior when 'rel' is selected as the step_calc
will be preserved for a release cycle. Where ever it is used, the following deprecation warning
will be raised:

    Warning. The method for computing relative step sizes is changing, switch to "rel_legacy" to keep
    the old behavior. In the next release, "rel" will be the same as "rel_avg".

In summary:

| step_calc       | Computed Step                                   |
| :---            |    :----:                                       |
| "rel_avg"       | Average absolute value of the vector.           |
| "rel_element"   | Absolute value of each vector element.          |
| "rel_legacy"    | Norm of the vector.                             |
| "rel"           | "rel_legacy" during transition, then "rel_avg"  |

