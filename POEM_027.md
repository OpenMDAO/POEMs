POEM ID:  027  
Title:   Approximation flag and state tracking  
authors: johnjasa   
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [#1492](https://github.com/OpenMDAO/OpenMDAO/pull/1492)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

Just as a user may want to know when a system is [under complex step](http://openmdao.org/twodocs/versions/latest/features/core_features/working_with_derivatives/approximating_partials.html?highlight=under_complex#complex-step), it's helpful to know when the system is under approximation of any kind. This would allow users to add logic in their `compute()` statements depending on if the system is under approximation or not.

Description
-----------


The changes required to the codebase are relatively straightforward and have been implemented in a [PR to OpenMDAO](https://github.com/OpenMDAO/OpenMDAO/pull/1492) already.

This PR adds a flag for all systems that is True when the system is under approximation, and False when it is not. Additionally, this PR adds `iter_count_without_approx` to systems, which counts the number of times `compute()` has been called while not counting any `compute()` calls that have been called as part of an approximation. This allows the user to add logic to a system based on the number of analysis calls to it regardless of the approximation scheme used.

I've added a test for the counting and the relevant docstrings. Feel free to suggest any syntax or docs as needed.
