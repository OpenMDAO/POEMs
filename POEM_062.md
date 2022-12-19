POEM ID: 062  
Title:  Stricter Option Naming  
authors: @naylor-b  
Competing POEMs:     
Related POEMs:    
Associated implementation PR: [#2378](https://github.com/OpenMDAO/OpenMDAO/pull/2378)  

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

This POEM proposes to force OpenMDAO option names to be restricted to valid python names, so that
they will work properly when passed as named arguments to the '__init__' methods of components,
drivers, etc.

There are a number of existing options that currently violate this restriction, so they would 
have to be changed, potentially breaking existing models.  This change would be implemented
initially by just issuing a deprecation warning stating that the option name is deprecated and
will result in an exception in a future release.

The following table shows which option names will be changed:

Option Name               | Class                           
:------------------------ | :-------------------------------
gradient method           | pyOptSparseDriver               
train:*                   | MetaModelUnStructuredComp       
train:*                   | MultiFiMetaModelUnStructuredComp
