POEM ID: 076  
Title:  Directional total derivative checks  
authors: kejacobson (Kevin Jacobson)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR:  

Status:

- [ ] Active
- [x] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

When performing a `check_totals` for arrays of design variables,
OpenMDAO will perform a finite difference for each element of the design variable array.
For expensive models with large design variable arrays, such as a finite element model
with 100s or 1000s of design variables, `check_totals` is not useful because it too slow.
Our current workaround is to manually perform total checks for a handful DVs 
with a finite difference of `run_model` compared to `compute_totals` or manually
do a directional derivative check.

## Description

The current POEM is proposing an bool option `directional` be added to `check_totals`, where
OpenMDAO will perform a single finite difference check perturbing all the variables specified in `wrt` 
with a random seed/direction vector.


```python
# given a model where struct_dvs is an array of design variables, the following would use a random perturbation
# vector to perform a single finite difference perturbation.
prob.check_totals(of='mass',wrt='struct_dvs', directional=True)

# Could specify multiple wrt variables and still perform a single perturbed model evaluation
prob.check_totals(of='mass',wrt=['struct_dvs', 'aero_dvs'], directional=True)
```
