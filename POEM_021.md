POEM ID: 021  
Title:  _post_configure moved to public API  
authors: robfalck (Rob Falck)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated


Motivation
----------

The _post_configure method is needed for components in which inputs and outputs are not directly added, such as
BalanceComp and AddSubtractComp.  For instance, if `bal.add_balance(...)` is called during configure, the component
must be able to respond accordingly.

Description
-----------

The `_post_configure` method is being moved to the public API (renamed `post_configure`).

Rejection Rationale
-------------------

This POEM is being rejected. After further consideration the development team has decided to go a different way.  _post_configure further complicates an already complex setup stack.
