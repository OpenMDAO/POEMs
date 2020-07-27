POEM ID:  29
Title:   Retrieval of IO Variable Metadata
authors: Bret Naylor   
Competing POEMs: N/A  
Related POEMs: N/A
Associated implementation PR: 

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

As a result of changes to the OpenMDAO setup stack, it's now possible to access variable metadata
from sub-groups and sub-components during `configure`.  The only functions that provide access
to some of that metadata currently are `list_inputs` and `list_outputs`, which return a list of 
(name, metadata) tuples as well as printing that information to an output stream.  However,
`list_inputs` and `list_outputs` are less flexible and have different default behaviors than would
be preferable for a metadata retrieval function called primarily from configure().  

Description
-----------

I propose taking the metadata retrieval part of `list_inputs`/`list_outputs` and putting it, with 
suitable defaults, into a function called `get_io_metadata`.  This function could be called directly 
from `configure` and would also be called internally from `list_inputs`/`list_outputs`.

The new function would be a method of `System` and would be defined as follows:

```
def get_io_metadata(self, iotypes=('input', 'output'), metadata_keys=None, 
                                   includes=None, excludes=(), 
                                   get_remote=False, rank=None)
```

The `iotypes` arg would allow the caller to specify where input variables, output variables, or
both (the default) were requested.

The `metadata_keys` would be an iterator of key names into the variable metadata dicts that would
be retrieved.  A value of None, the default, would indicate that all entries in the metadata dicts
would be retrieved.

The `includes` arg would be either None, indicating that all variables should be retrieved, or
an iterator of wildcard strings that, if matched by a variable name, would indicate that that 
variable's metadata would be returned in the metadata list, subject to the possibility of
being excluded by the `excludes` arg.

The `excludes` arg would be an iterator of wildcard strings that would exclude any matching
variable names from the metadata list.

The `get_remote` arg, if True, would cause metadata from all variables across all MPI processes
to be retrieved.  If False, only local values would be returned.

The `rank` arg would have no effect unless `get_remote` were True.  If so, a rank of None would
cause the metadata to be allgathered to all MPI processes.  Otherwise it would only be gathered 
to the specified rank.

The variable names returned in the metadata list would be the relative names.  For example,
if `get_io_metadata` were called on system `a.b.c`, the metadata entry for the variable 
`a.b.c.x.y.z.foo` would have the name `x.y.z.foo`.  Also included in every returned metadata
dict will be the entries `prom_name`, giving the promoted name in the scope of the `System`
indicated by `self`, and `discrete`, a boolean indicating whether the given variable is 
discrete or not.

