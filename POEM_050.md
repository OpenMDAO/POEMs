POEM ID: 050  
Title: Fix val/value inconsistency in the API  
authors: [robfalck]  
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

Multiple users have noted that OpenMDAO is a bit inconsistent in its API wrt the use of the terms `val` and `value` when providing values of variables.
This POEM aims to resolve this inconsistency.

Description
-----------

OpenMDAO uses the keyword `val` to specify that values are being provided in most places.
Notable exceptions are metadata for I/O which uses `value`, and (ironically) `set_val`, which uses the keyword argument `value`.

Use of `value` will still function, with deprecation warnings, until version 4.0.0, which is expected to be released in the summer of 2021.
At that point, all metadata references and keyword argument names which were previously `value` must be replaced with `val`.

Examples 
--------

`list_inputs` and `list_outputs` will change from `values=True` to `vals=True`. `values` will still be available but it will be deprecated.

```
prob.model.list_inputs(vals=True)
prob.model.list_outputs(vals=True)
```

`set_val` will also deprecate `value` in favor of `val`. Set `val` to your values to avoid deprecation warnings.

```
def set_val(self, name, value=None, units=None, indices=None, val=None):
```


Backwards Compatibility
------------------------

This change will be backwards incompatible.
Deprecations will be put in place such that `value` will work as it currently does until the OpenMDAO 4.0.0 release.
