POEM ID: 041  
Title: Add expressions to ExecComp after instantiation  
authors: [@robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [#1977](https://github.com/OpenMDAO/OpenMDAO/pull/1977)

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation

Almost all OpenMDAO components allow for IO to be added after instantiation.
Currently, ExecComp does not; the handling of all IO is done in `setup`.
There are situations where an expression needs to be added at setup time.

## Description

This POEM proposes to add a new method to ExecComp: `add_expr`.
Add_expr will take the same form as ExecComp initialization:

```python
def add_expr(expr, **kwargs)
```

To make it usable during the configure step of setup, `add_expr` will immediately add the necessary IO and declare the relevant partials for the given expression.

## Example

```python
import openmdao.api as om
exec_comp = om.ExecComp()
exec_comp.add_expr('y = sin(x)', y={'shape': (5,)}, x={'shape': (5,)})
```

### Detecting inconsistent variable metadata

If added after the above example, the following should raise an error:

```python
exec_comp.add_expr('z = cos(x)', z={'shape': (6,)}, x={'shape': (6,)})
```

```bash
ValueError: Input x has multiple values for metadata: 'shape'
```


