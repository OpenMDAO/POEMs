POEM ID: 086  
Title: Top-level setting of system options.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [PR 2931](https://github.com/OpenMDAO/OpenMDAO/pull/2931)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [x] Integrated

## Motivation

Users have often complained that setting options throughout a system tree can
be onerous...passing values from a parent group to subgroup to components
can be a tedious, error-prone process.

## Proposed Solution

OpenMDAO already has a _problem_meta object that users could, if they wished to do so,
utilize for options to be passed to subsystems.

This document proposes using that mechanism explicitly for the purpose of passing options down
to subsystems.

1. OpenMDAO will add a new key `'model_options'` to `Problem._metadata`.

`model_options` will be a standard python dictionary keyed by a pathname filter.
Each value associated with a given pathname filter will be a dictionary of option names/values.

2. `model_options` is passed, with the rest of `Problem._metadata`, to all subsystems in the problem model.

During model setup, a model will try to match its pathname to each of the keys in `model_options`.
If its pathname matches, it will check the associated options names. If the model has the given option name, it will
override its current option value with the given value.
This all happens before the System's `setup()` method is called, giving the user to
override options that determine how the model systems are setup.

3. `Problem._metadata['model_options']` will be available as a property of Problem: `Problem.model_options`.

4. `Problem._metadata['model_options']` will be available as a property of each Group: `Group.model_options`.

This will allow systems to modify data in `model_options` that are passed to their children.
In this way, a Group can dictate which option values are sent to all of its descendent systems without the need to explicitly pass the option at each step along the way.

Consider the following code.
Assume each subsystem takes some options ('length', 'width', and 'height').
Whereas previously we would have to pass these options to each subsystem instantiation,
and then pass them to each child of the subgroups:

```python
import openmdao.api as om

class MyGroup(om.Group):
    
    def initialize(self):
        self.options.declare('length', types=float)
        self.options.declare('width', types=float)
        self.options.declare('height', types=float)
    
    def setup(self):
        length = self.options['length']
        width = self.options['width']
        height = self.options['height']
        
        self.add_subsystem('G1', GroupOne(length=length, width=width, height=height))
        self.add_subsystem('G2', GroupTwo(length=length, width=width, height=height))
        self.add_subsystem('G3', GroupThree(length=length, width=width, height=height))
        self.add_subsystem('C1', CompOne(length=length, width=width, height=height))
        self.add_subsystem('C2', CompTwo(length=length, width=width, height=height))
        self.add_subsystem('C3', CompThree(length=length, width=width, height=height))
```

this is now achievable with the somewhat more terse setup method:

```
    def setup(self):
        length = self.options['length']
        width = self.options['width']
        height = self.options['height']
        
        self.add_subsystem('G1', GroupOne())
        self.add_subsystem('G2', GroupTwo())
        self.add_subsystem('G3', GroupThree())
        self.add_subsystem('C1', CompOne())
        self.add_subsystem('C2', CompTwo())
        self.add_subsystem('C3', CompThree())
        
        # Send these options to all subsystems when setting them up.
        self.model_data[f'{self.pathname}.*'] = {'length': length,
                                                 'width': width,
                                                 'height': height'}
```

## Notes

Subsystems cannot simply pass their options onto their child components
because in many cases they have options with the same names but different values.

This still, unfortunately, does not reduce the burden of declaring many options in subsystems.
This is probably best left as a use-case for subclassing, where a System can acquire certain options be inheriting from some super class that only adds those options.

Using flat dictionaries here lends itself to putting model options
in a file format such as YAML or TOML. At this time we're not committing
to adding a dependency to OpenMDAO to do so, but users are welcome to do so on their own.
We may add such a standard approach when 3.11 (which includes TOML support) becomes the oldest supported Python version.

Dictionaries are now ordered in Python so for options provided in multiple matching path filters,
the latest one will take effect.

Systems will support this functionality through a `load_model_options` method.
Users may override this method to impose custom behavior.
