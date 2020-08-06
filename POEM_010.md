POEM ID: 010
Title: add argument `recordable` to options.declare
Authors: @robfalck
Competing POEMs: [N/A]  
Related POEMs: [N/A]  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

This POEM adds a minor non-breaking change to the user-facing API.

Motivation
==========
If a model has an option which is not pickleable, recording fails.
To get around this, OpenMDAO currently allows the `system.options['options_excludes'] = ['foo']` mechanism to prevent it from being recorded.
In some cases, such as the `guess_func` option for BalanceComp, this object will never be pickleable and therefore it shouldn't be the users responsibility to declare `options_excludes`.  
Instead, the option should be able to be marked as recordable (or not) when the option is declared.

Description
===========

This POEM proposes adding a new argument 'recordable' to `System.options.declare`.
It will default to True (the current behavior) and behave as if it is added to `system.options['options_excludes']` by default.

References
----------

N/A
