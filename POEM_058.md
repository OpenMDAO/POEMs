POEM ID: 058  
Title: Fixed grid interpolation methods  
authors: Kenneth-T-Moore  
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

The general table-based interpolation strategy in OpenMDAO is very flexible, but it is also slow, particularly
for higher-dimension tables and for models that require vectorization (i.e., vec_size greater than 1 on MetaModelSemiStructuredComp.)
We can provide a much faster interpolation if we create some new methods that are tailored to a specific grid dimension
with point locations and point values that do not change. Much of the performance gain comes from caching the coefficients
computed in any given cell, so that subsequent lookups are done with just a polynomial evaluation.


## Description

The new methods will be available on `MetaModelSemiStructuredComp` and `InterpND`, and their names will include "#D-" prepended to the
algorithm name. So, a fixed implementation of "akima" on a 1-dimensional grid will be called "akima-1D".

```python
comp = om.MetaModelSemiStructuredComp(method='3D-lagrange3', extrapolate=True)
```



