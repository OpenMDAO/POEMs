POEM ID: 045  
Title: Promote-as change  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated

A less drastic change to the API has been accepted in place of this POEM.


Motivation
----------

When using promotes, the user can currently use a wildcard to promote many, or all, inputs and/or outputs.
If the user has many variables to be promoted, but only a few to be renamed via "promote as", there's currently not a good way to do this.
The user's only option is to promote each input/output individually.
This POEM proposes allowing "promote_as" to be used alongside wildcards.

Description
-----------

When a user invokes promotion, OpenMDAO will first expand all wildcards.
Wildcards are not allowed in "promote_as" tuples.
Next OpenMDAO will iterate through any tuples found in the promotion list.
If the first element in a "promote_as" tuple is found in the expanded list, it is replaced with the "promote_as" tuple.
In this way, the "promote_as" specification takes precedence over any wildcards found.

In addition, we will allow multiple wildcards to match a single variable and not result in a collision, though this should result in a promotion-related warning being issued.
