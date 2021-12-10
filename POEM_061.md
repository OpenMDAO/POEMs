POEM ID: 061  
Title:  Stricter Option Naming  
authors: [Bret Naylor]  
Competing POEMs:     
Related POEMs:    
Associated implementation PR:  

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

This POEM proposes to force OpenMDAO option names to be restricted to valid python names, so that
they will work properly when passed as named arguments to the '__init__' methods of components,
drivers, etc.

There are a number of existing options that currently violate this restriction, so they would 
have to be changed, potentially breaking existing models.  This change would be implemented
initially by just issuing a deprecation warning stating that the option name is deprecated and
will result in an exception in a future release.

Some examples of options that will need to change are 'gradient method' in `pyOptSparseDriver` and
all of the 'train:*' options used with `MetaModelUnStructuredComp`.
