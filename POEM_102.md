POEM ID: 102  
Title:  Units by Connection capability  
authors: robfalck (Rob Falck)  
Competing POEMs: None  
Related POEMs:  None  
Associated implementation PR: N/A  

Status:  

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation

Currently Dymos uses a relatively complex introspection pass during setup/configure to try to determine
shapes and units of variables within the user's ODE system. The development of shape-by-connection in
OpenMDAO means that we could get rid of this complexity, except we still need to determine units of 
states, controls, etc. by examining the ODE.

In most cases, units _should_ be specified when inputs or outputs are declared in a component, because
most of the models we're modeling assume some set of units within the `compute` or `apply_nonlinear` methods.

However, there are some cases where this is not the case. Some examples are:
- dymos applies a nondimensional differentiation matrix to state values, in conjunction with a time transformation, to provide an approximation of the state rates. These state rates units are therefore a function of the state units and the time units of the input variables.
- So called "pass-through" components which simply echo input values to outputs can be useful in cases where NonlinearBlockGS iteration can be applied. In these cases, the units of the outputs are the same as the units of the corresponding inputs.

## Description

This POEM proposes the addition of `units_by_conn`, `compute_units`, and `copy_units` to mimick those used for shape information.
These units can be determined using the same graph algorithms that exist for determining shapes.

### Example

A notional example of the use is the following:

```python
class PassThruComp(om.ExplicitComponent):

    def initialize(self):
        """
        Declare component options.
        """
        self.options.declare(
            'grid_data', types=GridData,
            desc='Container object for grid info')

        self.options.declare(
            'state_options', types=dict,
            desc='Dictionary of state names/options for the phase')

    def add_input(self, name, **kwargs):
        """
        I/O creation is delayed until configure so we can determine shape and units.

        Parameters
        ----------
        phase : Phase
            The phase object that contains this collocation comp.
        """
        super().add_input(name, **kwargs)

        self.add_output(f'{name}_out', copy_shape=name, copy_units=name)


    def compute(self, inputs, outputs):
        outputs.set_val(inputs.asarray())
```
