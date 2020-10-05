POEM ID: 035  
Title: More generalized behavior in promoted inputs.  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

The current input promotion system has exposed an inconsistency that can cause confusion among users and makes certain connections impossible.

## Description

Currently, if a variable is promoted using src_indices and it receives no connection, an automatic IndepVarComp output is created for it using those source indices to infer its shape.
However, if an output is connected to it with some set of source indices, it currently generates an error.
The `src_indices` from the connect call and the promotes call may conflict, and this is currently an error.
This is a weakness in the current API.  A complex model may utilize src_indices deep within a nested system.
A user may unwittingly try to connect to that with `src_indices` and encounter an error.

![Current behavior for sizing a promoted input](POEM_035/current_behavior.png)

Instead, this POEM proposes making src_indices apply to each level of promotion.
During setup, OpenMDAO can then traverse the chain of connections and resolve which elements of the ultimate source end up where in the ultimate target.

### Proposals

1. `src_shape` is added as an argument to `promotes` and `add_subsystem` (when inputs are promoted), which specifies the apparent shape of the promoted input (if connecting to it) or the related AutoIVC output (if left unconnected).

2. If `src_indices` are specified, then `src_shape` must be specified to remove any ambiguity, and `src_indices` are relative to that `src_shape`.

3. If multiple variables are promoted to the same input but with different `src_indices`, this is legal as long as they specify the same `src_shape`.

4. `src_shape` becomes an argument to `set_input_defaults` to force a common shape in the input or auto_ivc output

5. `src_indices` becomes a deprecated argument in `add_input`.  Since they only come into play in promotion, `src_indices` are specified in `promotes` or `add_subsystem` (when inputs are promoted).
