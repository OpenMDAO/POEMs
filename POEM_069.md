POEM ID: 069  
Title: Declare residual names for implicit components  
authors: joanibal (Josh Anibal), eytanadler  (Eytan Adler)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2589](https://github.com/OpenMDAO/OpenMDAO/pull/2589) (Proposed) [#2709](https://github.com/OpenMDAO/OpenMDAO/pull/2709) (Implemented)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

In many cases, it does not make sense to name the residuals of an implicit component by its outputs.
Furthermore, the residual may not even depend on the state by which it is named.
Currently, the keys of the residual vector are automatically set to match the keys of the output vectors. 

This can cause confusion when working with implicit components.
Consider the following example from the [circuit analysis example](https://openmdao.org/newdocs/versions/latest/examples/circuit_analysis_examples.html):

```python
class Node(om.ImplicitComponent):
    """Computes voltage residual across a node based on incoming and outgoing current."""

    def initialize(self):
        self.options.declare('n_in', default=1, types=int, desc='number of connections with + assumed in')
        self.options.declare('n_out', default=1, types=int, desc='number of current connections + assumed out')

    def setup(self):
        self.add_output('V', val=5., units='V')

        for i in range(self.options['n_in']):
            i_name = 'I_in:{}'.format(i)
            self.add_input(i_name, units='A')
            self.declare_partials('V', i_name, val=1)

        for i in range(self.options['n_out']):
            i_name = 'I_out:{}'.format(i)
            self.add_input(i_name, units='A')
            self.declare_partials('V', i_name, val=-1)

    def apply_nonlinear(self, inputs, outputs, residuals):
        residuals['V'] = 0.
        for i_conn in range(self.options['n_in']):
            residuals['V'] += inputs['I_in:{}'.format(i_conn)]
        for i_conn in range(self.options['n_out']):
            residuals['V'] -= inputs['I_out:{}'.format(i_conn)]
```

In this Node component the residual is the net current at the node.
Yet the key for the residual is `V` because it is set using the output variable names. 
It would be more intuitive to name the residual `I_net`. 

In multiple dimensions, this connection between output/state name and residual name becomes even more confusing.

```python

class Confusing(om.ImplicitComponent):
    def setup(self):
        self.add_output("x")
        self.add_output("y")

        self.declare_partials("x", ["x", "y"])
        self.declare_partials("y", ["x"])

    def apply_nonlinear(self, inputs, outputs, residuals):
        x = outputs["x"]
        y = outputs["y"]
        residuals["x"] = y * x - x ** 2
        residuals["y"] = x + 3.1416

    def linearize(self, inputs, outputs, partials):
        x = outputs["x"]
        y = outputs["y"]
        partials["x", "x"] = y - 2 * x
        partials["x", "y"] = x
        partials["y", "x"] = 1    
```

In this example, the fact that one residual is accessed with `"x"` and the other with `"y"` is arbitrary.
There is no apparent relationship between the output names and the residuals.
For example, `residuals["y"]` has no relation to `y`.
Declaring and implementing the derivatives can be even more confusing because the keys don't imply a relationship with the residuals.
A new user would look at `partials["x", "x"]` and wonder why it isn't equal to 1 (speaking from experience...).


## Proposed solutions

We propose adding the implicit component method `add_residual` to allow the user to explicitly declare the residuals.
This would decouple the residual names and shapes from the output names and shapes, making it more intuitive for new users.
Furthermore, this API modification is consistent with the way that inputs and outputs are declared and used by the methods.
The `add_residual` method would take the following arguments:
- `name`: residual name
- `shape`: (optional) residual shape
- `ref`: (optional) residual reference value, emulates what `res_ref` does in the `add_output` method
- `units`: (optional) residual units, emulates what `res_units` does in the `add_output` method
- `desc`: (optional) description of the residual to match interface of `add_input` and `add_output`


```python
class Node(om.ImplicitComponent):
    """Computes voltage residual across a node based on incoming and outgoing current."""

    def initialize(self):
        self.options.declare('n_in', default=1, types=int, desc='number of connections with + assumed in')
        self.options.declare('n_out', default=1, types=int, desc='number of current connections + assumed out')

    def setup(self):
        self.add_output('V', val=5., units='V')

        for i in range(self.options['n_in']):
            i_name = 'I_in:{}'.format(i)
            self.add_input(i_name, units='A')
            self.declare_partials('V', i_name, val=1)

        for i in range(self.options['n_out']):
            i_name = 'I_out:{}'.format(i)
            self.add_input(i_name, units='A')
            self.declare_partials('V', i_name, val=-1)
        
        self.add_residual('I_net', shape=1, ref=1.0, units='A', desc='net current flowing through the node')
        

    def apply_nonlinear(self, inputs, outputs, residuals):
        residuals['I_net'] = 0.
        for i_conn in range(self.options['n_in']):
            residuals['I_net'] += inputs['I_in:{}'.format(i_conn)]
        for i_conn in range(self.options['n_out']):
            residuals['I_net'] -= inputs['I_out:{}'.format(i_conn)]
```

This would also allow users to create a single residual vector with multiple outputs or multiple residual vectors with a single output.
The flexibility would enable users to name and define residuals that make more intuitive sense for their problem, even if the residual shape does not match the output shapes.

```python

class NotConfusing(om.ImplicitComponent):
    def setup(self):
        self.add_output("x")
        self.add_output("y")
        
        self.add_residual("r", shape=2)
        self.declare_partials("r", ["x", "y"])

    def apply_nonlinear(self, inputs, outputs, residuals):
        x = outputs["x"]
        y = outputs["y"]
        residuals["r"][0] = y * x - x ** 2
        residuals["r"][1] = x + 3.1416

    def linearize(self, inputs, outputs, partials):
        x = outputs["x"]
        y = outputs["y"]
        partials["r", "x"] = np.array([y - 2 * x, 1])
        partials["r", "y"] = np.array([x        , 0])
```
### Implementation ideas

The `add_residual` method would take in the residual name and the shape of the residual.
When `add_residual` is called, it would flip a switch in `ImplicitComponent` to indicate that the residuals have been named by the user.
If this switch is flipped, it will check that the total number of named residuals is the same as the total number of outputs added.
If this check passes it will allocate the residuals using the declared names and shapes. 
Otherwise, the residuals would be named by the outputs as they are now *to preserve backwards compatibility*. 

Our intention is not to affect the underlying data structure used to store the residuals, but to change the way the user accesses them within a component.
Under the hood this could use a mapping from the defined residual names back to some combination of the output names so accessing the data does not change.

We haven't attempted to implement this yet, but have sketched out some ideas in the associated draft PR.
