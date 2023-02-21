POEM ID: 079  
Title: Raise exception if the initial design point exceeds bounds.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2747](https://github.com/OpenMDAO/OpenMDAO/pull/2747)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

In complex optimizations it's not uncommon for the user to accidentally provide an initial value 
for a design variable that exceeds the bounds specified for that design variable.

Currently, OpenMDAO proceeds as if there is no problem in this situation, and in many cases the optimizer can succeed despite this.

But this is also indicative that the user didn't provide a good initial guess for their optimization problem.

## Proposed Solution

In this situation, the default behavior of OpenMDAO should be to issue a warning, given the liklihood that this will impact the user base.
In the future, we may change this behavior to raise an error by default.

- Checking for this behavior should be included in the run method of the optimization drivers along with testing for the absense of an objective.
- This check should issue a warning or raise an exception if any of the design variables has a value that exceeds the specified bounds.

The behavior will be impacted by the option `invalid_desvar_behavior` on the `Driver` class, which will accept values similar to those used by numpy.seterr.

1. `'warn'` : The default behavior, will issue a warning regarding all design variables that exceed their bounds.
2. `'raise'` : Will raise ValueError and issue a message regarding all design variables that exceed their bounds.
3. `'ignore'` : Ignores any design variables that exceed their bounds (the current behavior).

## Controlling behavior with an environment variable

For testing purposes, it may be useful to control this behavior globally.
This can be done using the environment variable: `OPENMDAO_INVALID_DESVAR_BEHAVIOR` which takes one of the above valid values.

## Other possible alternatives

We considered offering the ability to clip the offending design variable value to its acceptable range (IPOPT does this by default), but this is really an indication that the user hasn't specified the appropriate initial values for their optimization.

## Exception by default

After a few releases where warnings are issued, raising an exception will become the default behavior in OpenMDAO 3.25.0

## Prototype Implementation

The following is a notional implementation of `_check_invalid_desvars`.
This version prints out the offending design variable values and the corresponding bounds, but for design variables with a large number of elements this may not be the most useful way to present the information.

```python
from openmdao.utils.general_utils import env_truthy

class Driver(object):
    
    def _check_for_invalid_desvar_values(self):
        """
        Check for design variable values that exceed their bounds.

        This method's behavior is controlled by the OPENMDAO_INVALID_DESVAR environment variable,
        which may take on values 'ignore', 'error', 'warn'.
        - 'ignore' : Proceed without checking desvar bounds.
        - 'warn' : Issue a warning if one or more desvar values exceed bounds.
        - 'raise' : Raise an exception if one or more desvar values exceed bounds.

        These options are case insensitive.
        """
        if self.options['invalid_desvar_behavior'] != 'ignore':
            invalid_desvar_data = []
            for var, meta in self._designvars.items():
                val = self._problem().get_val(var, units=meta['units'])
                idxs = meta['indices']() if meta['indices'] else None
                scaler = meta['scaler'] or 1.
                adder = meta['adder'] or 0.
                lower = meta['lower'] / scaler - adder
                upper = meta['upper'] / scaler - adder

                if (val[idxs] < lower).any() or (val[idxs] > upper).any():
                    invalid_desvar_data.append((var, val, lower, upper))
            if invalid_desvar_data:
                s = 'The following design variable initial conditions are out of their ' \
                    'specified bounds:'
                for var, val, lower, upper in invalid_desvar_data:
                    s += f'\n  {var}\n    val: {val.ravel()}' \
                         f'\n    lower: {lower}\n    upper: {upper}'
                s += '\nSet the initial value of the design variable to a valid value or set ' \
                     'the driver option[\'invalid_desvar_behavior\'] to \'ignore\'.' \
                     '\'1\', \'true\', \'yes\', or \'on\'.'
                if invalid_desvar_option == 'raise':
                    raise ValueError(s)
                else:
                    issue_warning(s)
```

## Example

```python
import openmdao.api as om

# build the model
prob = om.Problem()

prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3'))

# setup the optimization
prob.driver = om.ScipyOptimizeDriver(invalid_desvar_behavior='raise')
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
  paraboloid.x
    val: [100.]
    lower: -50.0
    upper: 50.0
  paraboloid.y
    val: [-200.]
    lower: -50.0
    upper: 50.0
Set the initial value of the design variable to a valid value or set the driver option['invalid_desvar_behavior'] to 'ignore'.
```
