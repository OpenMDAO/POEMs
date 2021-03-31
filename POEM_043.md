POEM ID:  043  
Title:  No `src_indices` warning when both components are distributed   
authors: markleader (Mark Leader)  
Competing POEMs: 044  
Related POEMs: None  
Associated implementation PR: [#1915](https://github.com/OpenMDAO/OpenMDAO/pull/1915)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated



## Motivation

For optimization with distributed components, when `src_indices` are not set, a warning is printed. For example:

```
/usr/local/lib/python3.9/site-packages/openmdao/core/component.py:903: UserWarning:'dp' <class DistribParaboloid>: Component is distributed but input 'dp.w' was added without src_indices. Setting src_indices to np.arange(0, 1, dtype=int).reshape((1,)).
/usr/local/lib/python3.9/site-packages/openmdao/core/component.py:903: UserWarning:'dp' <class DistribParaboloid>: Component is distributed but input 'dp.x' was added without src_indices. Setting src_indices to np.arange(0, 3, dtype=int).reshape((3,)).
/usr/local/lib/python3.9/site-packages/openmdao/core/component.py:903: UserWarning:'dp' <class DistribParaboloid>: Component is distributed but input 'dp.w' was added without src_indices. Setting src_indices to np.arange(1, 2, dtype=int).reshape((1,)).
/usr/local/lib/python3.9/site-packages/openmdao/core/component.py:903: UserWarning:'dp' <class DistribParaboloid>: Component is distributed but input 'dp.x' was added without src_indices. Setting src_indices to np.arange(3, 5, dtype=int).reshape((2,)).
```


## Description
This POEM suggests removing the warning for variables which are connected between two distributed components. I think the behavior in that case will always be clear, so there does not need to be a warning, and removing warnings in these cases will reduce both user confusion and output to the command line.

In the case of a variable which is connected between a non-distributed component and a distributed component, I think the warning is helpful to clarify that the default behavior was what the user intended.


## Rejection Note: 

This POEM was rejected in favor of 044, which is more general and handles all the various OpenMDAO warnings. 