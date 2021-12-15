POEM ID:  055  
Title:  Min/Max Variable Print Option for Arrays  
authors: @andrewellis55(Andrew Ellis)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [#2280](https://github.com/OpenMDAO/OpenMDAO/pull/2280)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation
When printing various debugging data, be in from the debug print or from 
Problem.list_problem_vars(), we only have two options for arrays - Printing 
the magnitude or printing the entire array. However when dealing 
very large arrays with widely varying values, neither of these options provide 
a great quick visual reference of how the array is interacting with upper and 
lower bounds of a constraint. For this reason it is propsed that an additional 
option be given to print the min and max of a given array as this gives a better 
reference with repespect to upper and lower bounds.

## Problem Statement
It is propsed that an additional option be given to Problem.list_problem_vars() 
and possibly also the debug_print of the driver to print the min and max of a 
given array as this gives a better reference with repespect to upper and lower 
bounds.

## Example to illustratre where this becomes useful
Suppose we are constraining the stress of a component for a series of 
100 load cases, neither printing the array nor showing the magnitude gives 
a quick visual check as to whether the constraint is satisfied 

```python
import openmdao.api as om 
import numpy as np

np.random.seed(42)
num_loads = 100

class Stress(om.ExplicitComponent):

    def setup(self):
        self.add_input('radius', units='mm')
        self.add_input('forces', shape=(num_loads), units='kN')

        self.add_output('area', units='mm**2')
        self.add_output('stress', shape=(num_loads,), units='MPa')

    def compute(self, inputs, outputs):
        outputs['area'] = 3.14159 * inputs['radius']**2
        outputs['stress'] = inputs['forces'] / outputs['area']

prob = om.Problem()
model = prob.model

model.add_subsystem('stress', Stress(), promotes=['*'])
model.add_design_var('radius', lower=0)
model.add_constraint('stress', upper=10)
model.add_objective('area')

prob.setup()
prob.set_val('forces', (np.random.rand(num_loads)**3), units='MN')

prob.driver = om.ScipyOptimizeDriver()
model.approx_totals()

prob.run_driver()

prob.list_problem_vars(
    cons_opts=['lower', 'upper'],
    print_arrays=True
)

```

## Implentation 
The simplest implementatio would simply be an extension to the current interface to allow a call 
with the additional options `min` and `max` as seen bellow

```python
prob.list_problem_vars(
    desvar_opts=['min', 'lower', 'upper', 'max'],
    cons_opts=['min', 'lower', 'upper', 'max'],
    print_arrays=True
)
```

This would create two additional columns and thus the outputs from the above example would be similar 
to the output bellow

```
----------------
Design Variables
----------------
name    value         size  lower  min                max                upper  
------  ------------  ----  -----  -----------------  -----------------  ----- 
radius  [5.53128897]  1     0.0    5.531288965510812  5.531288965510812  1e+30  

-----------
Constraints
-----------
name           value                size  lower   min                     max               upper  
-------------  -------------------  ----  ------  ----------------------  ----------------  ----- 
stress.stress  |37.56105229124744|  100   -1e+30  1.7519214920178306e-06  9.99999999999987  10.0   

----------
Objectives
----------
name         value          size
-----------  -------------  ----
stress.area  [96.11744123]  1
```

## Pull Requests
PR #2240

