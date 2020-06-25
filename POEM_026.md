POEM ID: 026  
Title:   Remove support for factorial function in ExecComp  
authors: [swryan]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1483  

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

With version 1.5.0, SciPy enforces the integer datatype for arguments to the factorial function.

ExecComp is intended for continuous functions and relies on this assumption to calculate derivatives
via complex step. The factorial function does not satisfy this requirement and thus is not supported.

Description
-----------

Use of the factorial function in an ExecComp is deprecated for SciPy versions up to 1.5.0 and will
raise a RuntimeError for SciPy versions 1.5.0 and up, with an appropriate error message.
