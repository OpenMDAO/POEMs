POEM ID: 071  
Title: POEM_071 - Change ExecComp to use `declare_coloring`  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2696](https://github.com/OpenMDAO/OpenMDAO/pull/2696) 

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

The `ExecComp` in OpenMDAO uses complex-safe functions to provide user-defined calculations within a run script in leiu of writing a custom component.

The option `has_diag_partials` on ExecComp was added prior to the development of partial derivative coloring to provide a common sparsity pattern for vectorized components.

With the advent of partial coloring, `has_diag_partials` is no longer needed.
Users should be able to expect that `ExecComp` will determine the sparsity pattern of calculations involved.

### Leaving `has_diag_partials` capability in place.

Option `has_diag_partials` will remain in place.
Leaving the existing complex-step internals in place allows us to complex-step through the ExecComp without require that the entire model be allocated as complex.
Since diagonal partials is a common use case, using `has_diag_pargtials` can provide some performance improvement over computing the coloring dynamically.

### Default arguments are passed to `declare_coloring`

`declare_coloring` will be called with its default arguments.
If the user wishes, they may call `declare_coloring` on the ExecComp instance explicitly and pass it their desired arguments.
