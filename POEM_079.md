POEM ID: 079  
Title: Raise exception if the initial design point exceeds bounds.  
authors: [Rob Falck](https://github.com/robfalck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#TBD](https://github.com/OpenMDAO/OpenMDAO/pulls)  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

In complex optimizations it's not uncommon for the user to accidentally provide an initial value 
for a design variable that exceeds the bounds specified for that design variable.

Currently, OpenMDAO proceeds as if there is no problem in this situation, and in many cases the optimizer can succeed despite this.

But this is also indicative that the user didn't provide a good initial guess for their optimization problem.

## Proposed Solution

In this situation, the default behavior of OpenMDAO should be to raise an exception and stop.

- Checking for this behavior should be included in the run method of the optimization drivers along with teseting for the absense of an objective.
- This check should raise an exception if any of the design variables has a value that exceeds the specified bounds.
- Users may disable this check (and get the current behavior) by setting the environment variable `OPENMDAO_ALLOW_INVALID_DESVAR` to a value that is not "falsey," eg `'1'`, '`true'`', `'yes'`, or `'on'`.

**This POEM would change default behavior but allow it to be overridden to restore previous behavior.**

## Prototype Implementation

The following is a notional implementation of `_check_invalid_desvars`.
This version prints out the offending design variable values and the corresponding bounds, but for design variables with a large number of elements this may not be the most useful way to present the information.

```python
from openmdao.utils.general_utils import env_truthy

class Driver(object):
    
    def _check_for_invalid_desvar_values(self):
        if not env_truthy('OPENMDAO_ALLOW_INVALID_DESVAR'):
            desvar_errors = []
            for var, meta in self.driver._designvars.items():
                lower = meta['lower']
                upper = meta['upper']
                val = self.get_val(var, units=meta['units'])
                if (val < lower).any() or (val > upper).any():
                    desvar_errors.append((var, val, lower, upper))
            if desvar_errors:
                s = 'The following design variable initial conditions are out of their specified bounds:'
                for var, val, lower, upper in desvar_errors:
                    s += f'\n {var}\n    val: {val.ravel()}\n    lower: {lower}\n    upper: {upper}'
                s += '\nSet the initial value of the design varaible to a valid value or set the environment variable ' \
                     'OPENMDAO_ALLOW_INVALID_DESVAR to \'1\', \'true\', \'yes\', or \'on\'.'
                raise ValueError(s)
```

## Example

```python
import openmdao.api as om

# build the model
prob = om.Problem()

prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3'))

# setup the optimization
prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'

prob.model.add_design_var('paraboloid.x', lower=-50, upper=50)
prob.model.add_design_var('paraboloid.y', lower=-50, upper=50)
prob.model.add_objective('paraboloid.f')

prob.setup()

# Set initial values.
prob.set_val('paraboloid.x', 103.0)
prob.set_val('paraboloid.y', -400.0)

# run the optimization
prob.run_driver();
```

Outputs

```text
ValueError: The following design variable initial conditions are out of their specified bounds:
 paraboloid.y
    val: [-400.]
    lower: -50.0
    upper: 50.0
Set the initial value of the design varaible to a valid value or set the environment variable OPENMDAO_ALLOW_INVALID_DESVAR to '1', 'true', 'yes', or 'on'.
```
