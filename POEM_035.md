POEM ID: 035  
Title: More generalized behavior in promoted inputs.  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


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

1. `src_shape` is added as an argument to `promotes` and `set_input_defaults` (when inputs are promoted), which specifies the apparent shape of the promoted input (if connecting to it) or the related AutoIVC output (if left unconnected).

2. If multiple inputs are promoted to the same name then their `src_shape` must match, but their `src_indices` may be different.

3. `src_indices` becomes a deprecated argument in `add_input`.  Since they only come into play in promotion, `src_indices` are specified in `promotes`.  `src_indices` are NOT a valid argument to `set_input_defaults`.
