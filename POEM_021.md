POEM ID: 021  
Title:  _post_configure moved to public API
authors: [robfalck] (Rob Falck)  
Competing POEMs: N/A
Related POEMs: N/A
Associated implementation PR: N/A

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

The _post_configure method is needed for components in which inputs and outputs are not directly added, such as
BalanceComp and AddSubtractComp.  For instance, if `bal.add_balance(...)` is called during configure, the component
must be able to respond accordingly.

Description
-----------

The `_post_configure` method is being moved to the public API (renamed `post_configure`).

This API change is being accepted upon creation, and included as a POEM to inform the community of the change.