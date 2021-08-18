POEM ID: 054  
Title: Specifying source array as flat or non-flat when setting src_indices or dv or constraint indices  

Authors: [naylor-b]  

Competing POEMs: N/A  

Related POEMs: N/A  

Associated implementation PR: #  

Status:  

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation  

In POEM 53, we modified the behavior of indexing to mimic the way indexing behaves when applied
to numpy arrays, but in the process of doing this we accidentally left out certain behaviors
related to indexing into a non-flat source array.  In the existing implementation, if
an index is flat, for example, [1], or [2, 4, 6], the source array is assumed to be flat,
but indexing into a numpy array doesn't behave that way.  For example, when indexing into
a 3x3 numpy source array, an index of [1] would result in a 1x3 array, but using that same
[1] to index into an openmdao array would result in a size 1 array.


## Description  

Indexing in openmdao appears in 2 groups of methods. The first group, `Group.connect`, `Group.promotes`,
and `Component.add_input`, all have a `src_indices` argument that specifies how an input variable
is connected to its source variable.  These methods also have a `flat_src_indices` argument that,
if True, will specify that the indices are assumed to index into a flattened source.  By setting
this argument appropriately the user can get either the old openmdao behavior (flat_src_indices=True),
or the more numpy-like behavior (flat_src_indices=False).

The second group, `System.add_design_var`, `System.add_constraint`, and `System.add_objective`,
all specify which part of a given output variable should be used by openmdao as a design variable,
constraint, or objective.  These methods have a `indices` argument (or an `index` argument for
`add_objective`) to specify which part, and a new argument, `flat_indices`, will be added to
allow the user to have the same flexibility as in the first group of methods mentioned above.

Note that one difference between these two groups of methods is that the default value of
`flat_src_indices` from the first group is `None`, while the default value of `flat_indices`
in the second group is `True`.  This was done in an attempt to minimize the number of changes needed
to existing models.

Note also that `flat_src_indices` and `flat_indices` only have meaning for indices that appear
flat.  For example, setting `flat_src_indices=True` for `src_indices=om.slicer[:, 2]` doesn't
make any sense because the source array in that case would have to have at least 2 dimensions in
order for the index to be valid.

If a model breaks with this change, fixing it should require nothing more than adding `flat_src_indices=True`
to any `connect`, `promotes`, or `add_input` commands that involve a non-flat source array and
an apparently flat `src_indices` array.
