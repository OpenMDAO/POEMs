POEM ID: 066  
Title: Adopt NEP29  
authors: @robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

To date OpenMDAO has supported Python versions until they are officially unsupported by the Python software foundation.
This has occasionally led to issues with dependency conflicts and other troubles for our oldest supported Python version.
This POEM recommends that OpenMDAO, as numpy-dependent software, adopt the numpy deprecation policy: [NEP-0029](https://numpy.org/neps/nep-0029-deprecation_policy.html).

## Implementaiton

This implementation will occur in the next minor release of OpenMDAO after the integration of this POEM.
Python and Numpy support for various versions will be dropped per the table at the NEP-0029 link above.
