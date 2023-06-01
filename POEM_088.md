POEM ID: 088  
Title: User-configurable load_case functionality.   
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  N/A  
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

In some applications, the idea of changing the size of the systems involved in an OpenMDAO run are important.
One use is the notion of grid-refinement in dymos.
We solve the problem by discretizing the time-history into a certain number of nodes, assess the error in the solution, and then solve the problem again with a different number of nodes until the assessed error is within tolerance.
Another use-case might be jump-starting a dymos optimization with a previous "close" solution.

The current `load_case` fails if the size of the variable differs from the size of the corresponding variable in the case being loaded.
The Phase class in dymos has enough information to know how to perform this interpolation, but currently `load_case` is using `set_val` at the problem level, and `Problem` knows nothing about the interpolation that needs to be performed.

## Proposed Solution

### OpenMDAO Implementation

The current `load_case` function in the `Problem` class will be updated to allow for the model or any of it's subsystems to have a custom `load_case` function.

The new `load_case` function on `Problem` will perform similarly as it does now by populating the input and output values in the model _except_ for values that belong to a System that provides it's own `load_case` method.

The base `System` class will get a default `load_case` method which a user must override in a subclass (Group or Component) to provide custom logic.

### Dymos Implementation

To test this implementation, on the Dymos side, the `Phase` class will reimplement `load_case`.
This implementation of `load_case` will call corresponding load_case methods in each transcription class, since how to allocate the data will be transcription-dependent.

We'll start with Radau, since it is the simplest transcription to deal with.
We can determine which inputs/outputs in the system are sized with `num_nodes` as the first dimension.
For ODE's, we will assume that all inputs whose first dimension is sized > 1 is sized with `num_nodes`.
The user will tag inputs/outputs in their system with `'dymos.static_target'` if they are vectors but not sized according to the number of nodes (the ambiguous case).

We will take the data that pertains to the subsystems within the Phase, interpolate it onto the number of nodes used within the phase (which may differ from that used in the Case), and pass that resulting data to the child subsystems `load_case` methods.

Once that's done, we should be able to use the openmdao `load_case` function with Dymos, and not have to keep using our adhoc implementation that's currently in dymos.
