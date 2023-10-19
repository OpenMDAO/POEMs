POEM ID:  078  
Title: Add ability to filter inputs to only those that are connected to IndepVarComp.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [PR 2813](https://github.com/OpenMDAO/OpenMDAO/pull/2813)  


Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation
User's have requested a way of knowing which inputs they are ultimately responsible for setting.
The recently implemented inputs report achieves this in a graphical format, but there is also some desire to do this programmatically.

## Description
It makes sense to implement this capability as part of `System.list_inputs`.
This POEM proposes the following new arguments

The first is `is_indep_var`:
```
is_indep_var : bool or None
    If None (the default), do no additional filtering of the inputs.
    If this is set to True, then list_inputs will only list those inputs which are connected to an output that is tagged with `openmdao:indep_var`.
    If set to False, it will only show those inputs that are _not_ connected to outputs tagged with `openmdao:indep_var`.
```

The second new argument to `list_inputs` is `is_design_var`.

```
is_design_var : bool or None
    If None (the default), do no additional filtering of the inputs.
    If this is set to True, then list_inputs will only list those inputs which are connected to outputs that are design variables for the driver.
    If set to False, it will only show those inputs that are _not_ connected to outputs that are not design variables for the driver.
```

Therefore, running

```python
p.model.list_inputs(is_indep_var=True)
```

will provide inputs that the user can ultimately change, though some of them maybe be overridden by the Driver as design variables.
Running

```python
p.model.list_inputs(is_indep_var=True, is_design_var=False)
```

Will show those variables that should be set by the user and whose values will not be overridden by the Driver.
