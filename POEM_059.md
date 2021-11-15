POEM ID: 0579 
Title:  Unitless And Percentage Based Units  
authors: Andrew Ellis 
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

This PEOM relates to the introduction of a defined dimentionless unit and units for
percentages.  

Often times quantities in engineering such as ratio are by definiton unitless 
quantities. When working in large teams, it is not uncommen for someone to 
accidentally connect a dimentional value to a dimentionless value. This is raised
as a warning, but is not explicitly forbidden the way connecting something with
different units would be.

Furthermore on the topic of units, percentages are frequently used in engineering.
While sometime the percentage representation is the best representation, sometimes
a decimal representation can be preferable. This POEM proposes a unit set for 
percentages that allows these to be interchangeable


## Summary of Changes to add Unitless Quantities

The following lines (with the nomenclature up for discussion) can be added to the unit_library.ini file

```
# Unitness
Unitless: none
```

Given the classes defined as 

```pyton
import openmdao.api as om

class Diameter(om.ExplicitComponent):

    def setup(self):

        self.add_output('diameter', units='m')

class DiameterRatioA(om.ExplicitComponent):

    def setup(self):

        self.add_output('diameter_ratio_a', units='none')

class DiameterRatioB(om.ExplicitComponent):

    def setup(self):

        self.add_input('diameter_ratio_b', units='none')
```

The following code may run

```python
prob = om.Problem()
prob.model.add_subsystem('D', Diameter(), promotes=['*'])
prob.model.add_subsystem('D_ratio_a', DiameterRatioA(), promotes=['*'])
prob.model.add_subsystem('D_ratio_b', DiameterRatioB(), promotes=['*'])
prob.model.connect('diameter_ratio_a', 'diameter_ratio_b')

prob.setup()
```

While the below code that mistakenly connects the dimater to the diameter ratio
will not

```python
prob = om.Problem()
prob.model.add_subsystem('D', Diameter(), promotes=['*'])
prob.model.add_subsystem('D_ratio_a', DiameterRatioA(), promotes=['*'])
prob.model.add_subsystem('D_ratio_b', DiameterRatioB(), promotes=['*'])
prob.model.connect('diameter', 'diameter_ratio_b')

prob.setup()
```

and result in the following error

```
RuntimeError: <model> <class Group>: Output units of 'm' for 'D.diameter' are incompatible with input units of 'none' for 'D_ratio_b.diameter_ratio_b'.
```

## Summary of Changes to add Percent Quantities

The following lines (with the nomenclature up for discussion) can be added to the unit_library.ini file

[base_units] - # Other
```
percent: percent
```

And 

[units] - # Other miscellaneous
```
dec: 100*percent, decimal representation of percent
```

This will allow use of percent to dec conversions as seen below

```pyton
import openmdao.api as om


class DectoPercent(om.ExplicitComponent):

    def setup(self):

        self.add_input('val', units='percent')


if __name__ == '__main__':

    prob = om.Problem()
    prob.model.add_subsystem('val_comp', DectoPercent(), promotes=['*'])

    prob.setup()
    prob.set_val('val', 10, 'percent')

    print('Dec: ', prob.get_val('val', 'dec'))
    print('%: ', prob.get_val('val', 'percent'))
```

## Main Topic of Discussion
I'm not 100% sure how I feel about the nomclature I've used above so I've very 
open to suggestions. I tried using the % sign in the unit_library.ini to no avail,
but if that were possible it would probably be the cleanest implentation for percentages.