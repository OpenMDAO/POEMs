POEM ID: 109  
Title:  Allow an Alias for an Input/Output to be Defined at the Component Level  
authors: Kenneth-T-Moore (Kenneth Moore)  
Competing POEMs: None  
Related POEMs:  https://github.com/OpenMDAO/POEMs/pull/217  
Associated implementation PR:  N/A  

Status:  

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation

Several major applications have taken advantage of OpenMDAO's lax restrictions on variable names by including a colon (:) in component input or output names, where the colon is a separator between different levels of an alternative data hierarchy that is not reflected in the model structure. For example, `Aviary` has a variable "aircraft:wing:span", which represents a variable of the form "system:subsystem:var". The advantage of this approach is that it allows a component writer to specify the exact input or output they want without needing to know the structure of the entire model, as long as we are starting with a well-defined hierarchy. Another advantage is that it allows other queries like promotions to target parts of the hiearchy, such as `promotes_inputs=["aircraft:*"]`.

Unfortunately, ":" is not a valid python name. This doesn't matter for most of OpenMDAO because the internal representation is a string, which is valid datatype. However, it matters at the `Component` level, and is a roadblock that prevents even considering improvements such as [POEM 108: Using the pydantic package to add serialization/deserialization and validation](https://github.com/OpenMDAO/POEMs/pull/217) to allow models to be serialized. There are other cases in OpenMDAO that required a workaround (e.g., "primal" name in jax.)

## Description

The goal of this enhancement is to allow the colon (:) to remain valid at the group and problem levels, allow the user to reference a hiearchy variable while defining I/O for a component, and require the internally-stored variable to be pythonic. This can be done simply by adding an alias argument:

```python
self.add_input('chord', val=3.5, units='m**2', alias="aircraft:wing:chord")
self.add_output('drag', val=3.5, units='m**2', alias="mission:summary:chord")
```

Note that the full alias is unique in the data hierarchy, but the pythonic name on the component does not have to be unique. Any openmdao interaction with this component will use the alias:

```python
self.connect('mycomp.x', 'wing_drag.aircraft:wing:chord')
```

But any internal operations use the pythonic name:

```python
def compute(self, inputs, outputs):

    # NOTE: We could probably use "drag.aircraft.chord" here, but should we?
    # We will need to investigate this. To make things "compatible" with jax, we should probably stick with the pythonic name in all functions, but this is an open discussion.
    chord = inputs['chord']
    outputs['drag'] = 2.0 * chord
```

And most importantly, serialization and jax primals of this component will use the pythonic name.

The component-level alias replaces a group promote+alias in certain situations such as this:

```python

# Old
excomp = ExecComp('y=2*x',
                   x={'val': 7}
self.add_subsystem("exec", execomp,
                   promotes_inputs=[('x', "aircraft:veritcal_tail:width")],
                   promotes_outputs=['*'],
                 )
# New
excomp = ExecComp('y=2*x',
                   x={'val': 7, alias="aircraft:veritcal_tail:width"}
                 )
self.add_subsystem("exec", execomp, promotes=['*'])
```


Component options also suffer from the same issue, so this enhancement also adds an alias to those:

```python
self.options.declare('num_passengers', default=100, alias="aircraft:crew_and_payload:num_passengers")
```

This will finally allow the following, which breaks if there is a colon in the name:

```python
MyComponent(num_passengers=3)
```

