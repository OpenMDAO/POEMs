POEM ID: 100  
Title: Input checking utility  
authors: lamkina (Andrew Lamkin)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: N/A  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation
Setting up and running OpenMDAO models often involves changing the default value of component inputs.
As models grow in complexity, the number of inputs grows rapidly, quickly increasing the difficulty of tracking default vs. user-set inputs.
Currently, there is not a utility that compares the default component inputs against user-set inputs with a filterable report.
This POEM proposes to create a utility to check the inputs before the `run_model` call to clearly expose the default and user-set inputs for debugging.

## Description
I suggest a utility that caches the default input values as metadata upon creation of a component.
Then, the utility will query the cache right before `run_model` and compare the current value of each input against the cache value.
Using that information, the utility outputs a report showing the user-set inputs and highlights any inputs that retained a default value.
The report will adopt the html format of the `check_connections` utility and offer similar filter capability, as well as a color scheme for quickly identifying the source of each input value.

To establish a color scheme, I split the input values into three categories:
1. Default inputs: These are established when `setup` is called on the component.
2. Intermediate inputs: These are changed by a group above the component during the `setup` or `configure` phases.
3. User inputs: These are changed by the user after `setup` and `configure`, but before `run_model`.

I suggest white to signify default inputs, yellow for intermediate inputs, and blue for user inputs.

I also suggest including detailed filtering capability for the html report.
The filter should have the following functionality:
1. Filter by exact variable path name.
2. Filter by glob pattern.
3. Filter by input category (listed above).
4. Filter by input value.
5. Filter by input for implicit or explicit components.

This utility can be a command line tool `openmdao check_inputs <script.py>`, or an optional feature that can be turned-on during the `setup` call with an argument of `setup(check="inputs")`

## Example

In the following example, the interface change is minimal, with only an optional `check="inputs"` argument added to the `setup` call.
I added comments to show the delineation between `Default`, `Intermediate`, and `User` inputs for this case.
The `ExampleGroup` is only included to show the `Intermediate` inputs and is not used in the script.
The result of running this script with `check="inputs"` would be an html report that is similar to existing OpenMDAO reporting formats.

```python
class Paraboloid(om.ExplicitComponent):
    """
    Evaluates the equation f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3.
    """

    def setup(self):
        self.add_input('x', val=0.0) # Default inputs
        self.add_input('y', val=0.0) # Default inputs

        self.add_output('f_xy', val=0.0)

    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        """
        f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3

        Minimum at: x = 6.6667; y = -7.3333
        """
        x = inputs['x']
        y = inputs['y']

        outputs['f_xy'] = (x - 3.0)**2 + x * y + (y + 4.0)**2 - 3.0

#######################################################################################
# Included only for illustrating the intermediate inputs (not used in the script below)
#######################################################################################
class ExampleGroup(om.Group);
    def setup(self):
        self.add_subsystem("parab_comp", Paraboloid())
        self.set_input_default("x", val=10.0) # Intermediate input

if __name__ == "__main__":
    model = om.Group()
    model.add_subsystem('parab_comp', Paraboloid())

    prob = om.Problem(model)
    prob.setup(check="inputs") # Input checking turned on

    prob.set_val('parab_comp.x', 3.0)   # User inputs
    prob.set_val('parab_comp.y', -4.0)  # User inputs

    prob.run_model()
    print(prob['parab_comp.f_xy'])

    prob.set_val('parab_comp.x', 5.0)   # User inputs
    prob.set_val('parab_comp.y', -2.0)  # User inputs

    prob.run_model()
    print(prob.get_val('parab_comp.f_xy'))
```