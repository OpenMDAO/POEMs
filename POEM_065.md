POEM ID: 065  
Title: Add a 'proc_group' option to add_subsystem  
authors: @naylor-b  
Competing POEMs:  
Related POEMs:  
Associated implementation PR:

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

OpenMDAO currently has no way to specify that multiple subsystems of a ParallelGroup should be allocated
on the same subset of processes, at least in the case where there are a number of procs allocated that
is equal to or greater than the number of subsystems.  In this case currently, OpenMDAO will allocate
at least one proc to each subsystem.  This can be wasteful in cases where a subset of the subsystems
run more quickly than the rest, such that even when running serially, that subset might take no longer
than any of the other subsystems take when running in parallel.


## Proposed solution

Adding a 'proc_group' option to add_subsystem provides a way for a user to specify that multiple 
subsystems should be allocated on the same process or set of processes.  This would allow all of the
'quick' subsystems in the case mentioned above to be all allocated on a single process, freeing up
more avilable processes to be allocated to the remaining subsystems.


## Example

Suppose we have a ParallelGroup with 6 subsystems, and 4 of them run much faster than the other 2,
and assume that we have 8 MPI processes available.  Using a proc_group, we could force the 4 quick
subsystems to be allocated on a single process, leaving the other 7 processes to be divided between the 2
remaining slower subsystems.


```
par = om.ParallelGroup()

# these 4 components are the 'quick' ones that we want to group together onto a single proc,
# so we put them in the same proc_group and set their max_procs to 1.
par.add_subsystem('C1', Comp1(), max_procs=1, proc_group='quick')
par.add_subsystem('C2', Comp2(), max_procs=1, proc_group='quick')
par.add_subsystem('C3', Comp3(), max_procs=1, proc_group='quick')
par.add_subsystem('C4', Comp4(), max_procs=1, proc_group='quick')

# let's assume that C5 requires twice as many procs as C6, so set proc_weights accordingly
par.add_subsystem('C5', Comp5(), proc_weight=2.0)
par.add_subsystem('C6', Comp6(), proc_weight=1.0)
```

Note that if multiple subsystems share the same proc_group, then their values (if any) for 
min_procs, max_procs, and proc_weight must match or an exception will be raised.

