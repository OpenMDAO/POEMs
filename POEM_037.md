POEM ID:  037  
Title: Give list_problem_vars the option to output unscaled variables.  
authors: Kenneth-T-Moore (optional real name)  
Competing POEMs: [list any other POEMs which are incompatible with this one]  
Related POEMs: [list any other POEMs which are related (but still compatible) with this one]  
Associated implementation PR:  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

The `list_problem_vars` method on Problem is useful for giving a concise summary of all the driver
variables (design variables, objective, constraints) at the end of an optimization. However, the
values it prints are the scaled values that the optimizer sees. When using this as a summary, it
would be useful to see the unscaled values.

## Description

The easiest way to do this is to add the argument "scaled" to the call. If you set this to False,
the values are printed unscaled. The default value is True, which prints the scaled value just like
the current implementation.


