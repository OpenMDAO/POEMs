POEM ID: 071  
Title: POEM_071 - Change ExecComp to use `declare_coloring`  
authors: @robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: N/A  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

The `ExecComp` in OpenMDAO uses complex-safe functions to provide user-defined calculations within a run script in leiu of writing a custom component.

The option `has_diag_partials` on ExecComp was added prior to the development of partial derivative coloring to provide a common sparsity pattern for vectorized components.

With the advent of partial coloring, `has_diag_partials` is no longer needed.
Users should be able to expect that `ExecComp` will determine the sparsity pattern of calualtions involved.

## Changes

1. `has_diag_partials` will be marked as deprecated but still be allowed as an option that does nothing.
2. `declare_coloring_kwargs` will allow the user to specify any arguments to be passed to [System.declare_coloring](https://openmdao.org/newdocs/versions/latest/features/experimental/approx_coloring.html#dynamic-coloring))

Since `declare_coloring` automatically does the work of `declare_partials`, this should simplify the code in `ExecComp` considerably.

## Open questions

Should `declare_coloring` only be called when there are multiple vector-valued inputs and outputs?
If yes, then do we retain the current system when all inputs/outputs are scalar, or just rely on `declare_coloring` to do the job for us?

I'm inclined to argue that partial coloring is fast and accurate enough that we shouldn't bother retaining the previous system as a fallback.

Any performance impacts due to this change will likely be negligible until the size of the input and output vectors grow very large.
Users who don't want to suffer such impacts are always free to implement their own component.
