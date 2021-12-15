POEM ID: 059  
Title:  Unitless And Percentage Based Units  
authors: Andrew Ellis  
Competing POEMs: N/A    
Related POEMs: N/A  
Associated implementation PR: [#2340](https://github.com/OpenMDAO/OpenMDAO/pull/2340)

##  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

This POEM relates to the introduction of a defined dimentionless unit and units for
percentages.  

Often times quantities in engineering such as ratio are by definition unitless
quantities. When working in large teams, it is not uncommon for someone to 
accidentally connect a dimensional value to a dimensionless value. This is raised
as a warning, but is not explicitly forbidden the way connecting something with
different units would be.

Furthermore on the topic of units, percentages are frequently used in engineering.
With the introduction of a 'unitless' quantity, a percentage could simply be defined
as a scalar of the unitless quantity.


## Summary of Changes to add Unitless Quantities

The following lines (with the nomenclature up for discussion) can be added to the unit_library.ini file

```
# Unitness
Unitless: unitless
```

Given the classes defined as 

```python
import openmdao.api as om

class Diameter(om.ExplicitComponent):

    def setup(self):

        self.add_output('diameter', units='m')

class DiameterRatioA(om.ExplicitComponent):

    def setup(self):

        self.add_output('diameter_ratio_a', units='unitless')

class DiameterRatioB(om.ExplicitComponent):

    def setup(self):

        self.add_input('diameter_ratio_b', units='unitless')
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


[units] - # Other miscellaneous
```
percent: unitless/100, percentage
```

This will allow use of percent to unitless conversions as seen below

```python
import openmdao.api as om

class MarginOfSafety(om.ExplicitComponent):
    def setup(self):
        self.add_input('stress', units='MPa', val=392)
        self.add_input('tensile_strength', units='MPa', val=400)

        self.add_output('margin_of_safety', units='unitless')

    def compute(self, inputs, outputs):
        stress = inputs['stress']
        tensile_strength = inputs['tensile_strength']
        outputs['margin_of_safety'] = tensile_strength / stress - 1

if __name__ == '__main__':

    prob = om.Problem()
    prob.model.add_subsystem('margin_comp', MarginOfSafety(), promotes=['*'])

    prob.setup()
    prob.run_model()

    print('Margin of Safety (decimal): ', 
          prob.get_val('margin_of_safety', units='unitless')[0])
    print('Margin of Safety (%)      : ',
          prob.get_val('margin_of_safety', units='percent')[0])
```
Which would give the output
```
Margin of Safety (decimal):  0.020408163265306145
Margin of Safety (%)      :  2.0408163265306145
```

## Main Topic of Discussion
I'm not 100% sure how I feel about the nomclature I've used above so I've very 
open to suggestions. I tried using the % sign in the unit_library.ini to no avail,
but if that were possible it would probably be the cleanest implentation for percentages.
