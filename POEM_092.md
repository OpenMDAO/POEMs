POEM ID: 092  
Title: User-defined function hook for pre-processing option set.  
authors: Kenneth-T-Moore (Ken Moore)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [PR 3040](https://github.com/OpenMDAO/OpenMDAO/pull/3040)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation

OpenMDAO's component options feature is sometimes used to define constant quantities with units. When coupled with
the top-level setting of system options, this creates as situation where an option might be specified in the
wrong units. As a general solution, this POEM proposes the addition of a pre-set function hook that the user
can define to pre-process a value and compute a new value before setting the option in a component. This hook
could be used to convert units, or it could be used for other processing.

## Proposed Solution

The only API change from this POEM is an additional argument to the `declare` method of OptionDictionary. The
new argument is "set_function", which takes a function whose input parameters are a dictionary that contains
the option's metadata and a value, and whose return is a new value.


## Example

```language=python
import openmdao.api as om
from openmdao.utils.units import convert_units


def units_setter(opt_meta, value):
    """
    Check and convert new units tuple into

    Parameters
    ----------
    opt_meta : dict
        Dictionary of entries for the option.
    value : any
        New value for the option.

    Returns
    -------
    any
        Post processed value to set into the option.
    """
    new_val, new_units = value
    old_val, units = opt_meta['val']

    converted_val = convert_units(new_val, new_units, units)
    return (converted_val, units)


class AviaryComp(om.ExplicitComponent):

    def setup(self):

        self.add_input('x', 3.0)
        self.add_output('y', 3.0)

    def initialize(self):
        self.options.declare('length', default=(12.0, 'inch'),
                             set_function=units_setter)

    def compute(self, inputs, outputs):
        length = self.options['length'][0]

        x = inputs['x']
        outputs['y'] = length * x


class Fakeviary(om.Group):

    def setup(self):
        self.add_subsystem('mass', AviaryComp())


prob = om.Problem()
model = prob.model

model.add_subsystem('statics', Fakeviary())

prob.model_options['*'] = {'length': (2.0, 'ft')}
prob.setup()

prob.run_model()
print('The following should be 72 if the units convert correctly.')
print(prob.get_val('statics.mass.y'))
print('done')
```


## Notes
