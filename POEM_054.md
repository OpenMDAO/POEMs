POEM ID: 054  
Title: Specifying source array as flat or non-flat when setting src_indices or dv or constraint indices  

Authors: [naylor-b]  

Competing POEMs: N/A  

Related POEMs: [https://github.com/OpenMDAO/POEMs/blob/master/POEM_053.md]  

Associated implementation PR: [#2279](https://github.com/OpenMDAO/OpenMDAO/pull/2279)

Status:  

- [ ] Active  
- [ ] Requesting decision  
- [ ] Accepted
- [ ] Rejected  
- [x] Integrated


## Motivation  

In POEM 53, we modified the behavior of indexing to mimic the way indexing behaves when applied
to numpy arrays, but in the process of doing this we accidentally left out certain behaviors
related to indexing into a non-flat source array.  In the existing implementation, if
an index is flat, for example, [1], or [2, 4, 6], the source array is assumed to be flat,
but indexing into a numpy array doesn't behave that way.  For example, when indexing into
a 3x3 numpy source array, an index of [1] would result in a 1x3 array, but using that same
[1] to index into an openmdao 3x3 array would result in a size 1 array.


## Description  

Indexing in openmdao appears in 2 groups of methods. The first group, `Group.connect`, `Group.promotes`,
and `Component.add_input`, all have a `src_indices` argument that specifies how an input variable
is connected to its source variable.  These methods also have a `flat_src_indices` argument that,
if True, will specify that the indices are assumed to index into a flattened source.  By setting
this argument appropriately the user can get either the old openmdao behavior (flat_src_indices=True),
or the more numpy-like behavior (flat_src_indices=False).  Note that specifying `src_indices` in
`Component.add_input` is deprecated and will be prohibited in some future release.

The second group, `System.add_design_var`, `System.add_constraint`, and `System.add_objective`,
all specify which part of a given output variable should be used by openmdao as a design variable,
constraint, or objective.  These methods have an `indices` argument (or an `index` argument for
`add_objective`) to specify which part, and a new argument, `flat_indices`, will be added to
allow the user to have the same flexibility as in the first group of methods mentioned above.

This POEM will be implemented in two parts.  The first part will we a transitional release that
will not break backwards compatability. It will add the new `flat_indices` argument and set its
default value, as well as the default value of `flat_src_indices` to None.  If the user does not 
set the `flat_*` flag value and the number of dimensions of the 
source array are greater then the number of dimensions indicated by the indices, a warning
will be issued describing the proper use of the `flat_src_indices` and `flat_indices` flags.
If the flag value is set to True, there will be no warning and the source array will be treated
as flat.  If the flat is set to False, an exception will be raised because internally the 
source array will still be treated as flat so setting `flat_*` to False isn't a valid option.

The next part will be a release that removes the deprecation warnings and changes the internal
behavior to no longer assume a flat source regardless of the number of dimensions of the indices.
The default values of `flat_src_indices` and `flat_indices` will be changed to False.  If a model
ran under the previous release *without any deprecation warnings* related to assuming a flat source,
then it should run without modification in this release.

Note also that `flat_src_indices` and `flat_indices` only have meaning for indices that appear
flat.  For example, setting `flat_src_indices=True` for `src_indices=om.slicer[:, 2]` doesn't
make any sense because the source array in that case would have to have at least 2 dimensions in
order for the index to be valid.  In cases like this, the flag values will be ignored and a warning
will be generated.

