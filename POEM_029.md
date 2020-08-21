POEM ID:  029  
Title:   Retrieval of IO Variable Metadata  
authors: [naylor-b] (Bret Naylor)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [#1577](https://github.com/OpenMDAO/OpenMDAO/pull/1577)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

As a result of changes to the OpenMDAO setup stack, it's now possible to access variable metadata
from sub-groups and sub-components during `configure`.  The only functions that provide access
to some of that metadata currently are `list_inputs` and `list_outputs`, which return a list of
tuples of variable names and associated metadata and print that information to an output stream.  However,
`list_inputs` and `list_outputs` are less flexible and have different default behaviors than would
be preferable for a metadata retrieval function called primarily from configure().  

The current versions of `list_inputs` and `list_outputs` only retrieve the variable 
values by default, and values will often not be needed in `configure`, where it's more likely
for entries like 'shape' to be needed.  Also, certain metadata items are not retrievable 
at all using `list_inputs` and `list_outputs`.  Finally, `list_inputs` and `list_outputs` always gather
or allgather the full value of distributed variables depending on the value of `all_procs`, but only if
`out_stream` is the default value or is not None.  The values of variables returned from 
`list_inputs` and `list_outputs` are always, however, just the local values.  This
behavior, where full distributed values are written to the output stream but only local values
are returned, could lead to confusion.  Also, using the default args would generate unwanted
output to stdout if called from `configure`, and could result in unnecessary gather/allgather of distributed 
values, which could be quite large.


Description
-----------

I propose taking the metadata retrieval part of `list_inputs`/`list_outputs` and putting it, with 
suitable defaults, into a function called `get_io_metadata`.  This function could be called directly 
from `configure` and would also be called internally from `list_inputs`/`list_outputs`.

The new function is a method of `System` and is defined as follows:

```
def get_io_metadata(self, iotypes=('input', 'output'), metadata_keys=None,
                    includes=None, excludes=None, tags=(), get_remote=False, rank=None,
                    return_rel_names=True):
```

The `iotypes` arg allows the caller to specify whether input variables, output variables, or
both (the default) are requested.

The `metadata_keys` are an iterator of key names into the variable metadata dicts to
be retrieved.  A value of None, the default, indicates that all entries in the 'allprocs'
metadata dicts are retrieved.  These metadata dicts contain 'units', 'shape', 'size', 'desc',
'ref', 'ref0', 'res_ref', 'distributed', 'lower', 'upper', and 'tags' for output variables
for example, and they can all be retrieved locally without additional gathers.
If 'values' or 'src_indices' are required, they must be explicitly requested, because for 
cases where values are distributed or remote, they must be gathered from other processes.

The `includes` arg is either None, indicating that all variables are retrieved, or
an iterator of wildcard strings that, if matched by a variable name, indicates that that 
variable's metadata is returned in the metadata list, subject to the possibility of
being excluded by the `excludes` arg.

The `excludes` arg is an iterator of wildcard strings that excludes any matching
variable names from the metadata list.

The `get_remote` arg, if True, causes metadata from all variables across all MPI processes
to be retrieved.  If False, only local values are returned.  Note that if neither `value` nor
`src_indices` are requested, then there is no need to retrieve any data from other
processes so no gathers/allgathers will need to be performed even if `get_remote` is True.

The `rank` arg has no effect unless `get_remote` is True.  If so, a rank of None causes the 
metadata to be allgathered to all MPI processes.  Otherwise it will only be gathered 
to the specified rank.

The `return_rel_names` arg, if True, will return relative variable names instead of 
absolute names.  The default is to return relative names. For example,
if `get_io_metadata` were called on system `a.b.c`, the metadata entry for the variable 
`a.b.c.x.y.z.foo` would have the name `x.y.z.foo`.  Also included in every returned metadata
dict are the entries `prom_name`, giving the promoted name in the scope of the `System`
indicated by `self`, and `discrete`, a boolean indicating whether the given variable is 
discrete.

Backwards Incompatibility
-------------------------

The behavior of list_inputs/list_outputs is changed such that the results are now returned where the path is relative to the model being interrogated.
list_inputs returns an absolute path relative to the model whose inputs are being requested.
list_outputs returns a promoted path relative to the model whose inputs are bing requested.
