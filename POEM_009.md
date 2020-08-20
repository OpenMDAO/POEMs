POEM ID: 009  
Title: setup/configure API Changes  
Authors: robfalck (Rob Falck)  
Competing POEMs: [N/A]  
Related POEMs: [003 - https://github.com/OpenMDAO/POEMs/pull/7]  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated

This POEM is being merged with 003 since it resolves the issues discussed there.

Motivation
==========
In complex models, setting up one component or system is often dependent
on the attributes of its children, but those are often not known at setup time.
To solve this, OpenMDAO provides a two-stage process:
  -  setup, which runs in a top-down manner (children of the current group have not yet been instantiated/setup)
  -  configure, which runs in a bottom-up manner (current system can interrogate properties of child subsystems)
While doing everything in a Group's setup method is fine for many cases, when
child-dependencies occur they must be resolved in configure.

Recent changes to the setup stack allow _almost_ everything that would typically
happen in setup to happen in configure, with the exception of adding subsystems.
That is, adding inputs and outputs to children, and issuing connections can now be done from configure.

Description
===========

This POEM proposes the following API changes to clarify the roles of setup and configure:
 - Calling a Group's add_subsystem method from configure will raise an exception.
 - A new method to promote IO within a system is needed so promotions can be issued in configure.
 - The current promotion mechanism via `add_subsystem` will remain in place.

The suggested signature of the Group method is

```
def promotes(subsys_name, any=None, inputs=None, outputs=None)

Parameters
----------
subsystem_path : str
    The name of the child subsystem whose inputs/outputs are being promoted.
any : Sequence of str or tuple
    A Sequence of variable names (or tuples) to be promoted, regardless 
    of if they are inputs or outputs. This is equivalent to the items 
    passed via the `promotes=` argument to add_subsystem.  If given as a
    tuple, we use the "promote as" standard of ('real name', 'promoted name')*[]: 
inputs : Sequence of str or tuple
    A Sequence of input names (or tuples) to be promoted. Tuples are
    used for the "promote as" capability.
outputs : Sequence of str or tuple
    A Sequence of output names (or tuples) to be promoted. Tuples are
    used for the "promote as" capability.
```

Promotes can only be used to promote directly from the children of the current
group (one step, no more).  Promoting things up a chain can be accomplished
by multiple calls.

This POEM is intended to address the issues discussed in POEM_003:  003 - https://github.com/OpenMDAO/POEMs/pull/7.

References
----------

N/A
