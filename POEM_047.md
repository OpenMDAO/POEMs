POEM ID:  047  
Title:  Component I/O independance from Problem Object  
authors: @andrewellis55(Andrew Ellis)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: #2005 (Implementation 1)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

Portions of this POEM were implemented, but others were rejected.
See notes under pull requests.

## Motivation
Most usage example of OpenMDAO are very script based rather than object
oreinted. When using OpenMDAO as part of a larger program, there can be some
interest in developing objects to encapsulate the optimization portions of one's
code. In order to preserve the "reconfigurability" (i.e. the ability to build
up OpenMDAO groups and components), one options is to build object that inherit
from OpenMDAO components themselves and extend the components in a manner to 
encapsulate the optimization problem and provide interfaces for user use. One of 
the key barriers preventing this is the difficulty classes may have with
accessing thier variable data after the problem has been run without referencing
the problem object.

## Problem Statement
It is proposed that a way for Components to access their own input / output data
independatly of the Problem object be created.


## Example to illustratre where this becomes useful
Suppose we have have a large OpenMDAO system called `ParabolaSystem`. In this
example it will only contain a few ExecComp and the Explicit Component 
`Parabola` but we can imagine in a real application it may contain many more 
components. 

We can imagine an application where there may be an interest to see how the 
`Parabola` can be optimized on it's own, and then following that see how the 
`ParabolaSystem` can be optimized as a whole. Typically this may be done with 
scripts that can perform each of these optimization, however an example is 
provided bellow where a `u_run_opt()` function has been added to each of the 
components (where the `u_` represents a user function) so that a user may run 
the optimization in a more object oriented manner without needing to understand 
the internals of OpenMDAO and optimization such as what optimizer to use.

Additionally, in order to allow users of the object to interface with the
results, the functions `u_plot()` and `u_print_eq()` have been added.

Note 1 that as the object still inherit from the base openmdao components, they
can still be added to OpenMDAO models/groups just like any other component.

Note 2 that it is NOT being proposed that `u_run_opt()` be added to that
standard framework, although the author has found it a useful way to package
optimizations.

```python
import openmdao.api as om 

class Parabola(om.ExplicitComponent):

    def __init__(self):
        super(Parabola, self).__init__()
        self.x = 0

    def set_x(self, x):
        self.x = x

    def setup(self):
        self.add_input('x', units='mm')
        self.add_input('a', units='mm')
        self.add_output('y', units='mm')
    
    def compute(self, inputs, outputs):
        x = inputs['x']
        a = inputs['a']
        y = (x-a)**2 + 4
        outputs['y'] = y

    def u_run_opt(self):
        prob = om.Problem()
        model = prob.model

        idv = model.add_subsystem('idv', om.IndepVarComp(), promotes=['*'])
        idv.add_output('x', val=self.x, units='mm')
        idv.add_output('a', val=1, units='mm')
        model.add_design_var('a')

        model.add_subsystem('parabola', self, promotes=['*'])
        model.add_objective('y')

        model.approx_totals()
        prob.driver = om.ScipyOptimizeDriver()
        prob.setup()
        prob.run_driver()

    def u_plot(self):
        pass

    def u_print_eq(self):
        pass

class ParabolaSystem(om.Group):

    def __init__(self):
        super(ParabolaSystem, self).__init__()
        self.p = Parabola()
        self.x0 = 0

    def set_x0(self, x0):
        self.x0 = x0

    def setup(self):
        self.add_subsystem('xx0', om.ExecComp('x = x0+7'), promotes=['*'])
        self.p = self.add_subsystem('parabola', self.p, promotes=['*'])
        self.add_subsystem('yy2', om.ExecComp('y2 = y+2'), promotes=['*'])

    def u_run_opt(self):
        prob = om.Problem()
        model = prob.model

        idv = model.add_subsystem('idv', om.IndepVarComp(), promotes=['*'])
        idv.add_output('x0', val=self.x0, units='mm')
        idv.add_output('a', val=1, units='mm')
        model.add_design_var('a')

        model.add_subsystem('parabolasys', self, promotes=['*'])
        model.add_objective('y2')

        model.approx_totals()
        prob.driver = om.ScipyOptimizeDriver()
        prob.setup()
        prob.run_driver()

    def u_plot(self):
        pass
    
    def u_print_eq(self):
        pass

if __name__ == '__main__':

    # The parabola object can be created and the operating parameter x can be 
    #   set as one typically would do in Object oriented programming
    p = Parabola()
    p.set_x(3)

    # A user function (designated by the u_) has been created so that a regular
    #   user can run the optimization without having to worry/know about the
    #   optimization specific settings. The puts the burden of deciding
    #   which optimizer to use, what tolerance, how to use indep var comps, etc
    #   on the programmer of the Parabola module, not the user of it
    p.u_run_opt()

    # Additionaly functions have been attached so that the user can see the 
    #   optimized results without needs to be aware of the problem strcture
    #   or even OpenMDAO at all. 
    p.u_plot()
    p.u_print_eq()

    # The same can also be done for the larger system
    ps = ParabolaSystem()
    ps.set_x0(3)
    ps.u_run_opt()
    ps.u_plot()
    ps.u_print_eq()

    # Once the large system has been optimized, the parabola inside the larger
    #   system can be returned and used in the same manner as the original 
    #   parabola object
    p2 = ps.p
    p2.u_plot()
    p2.u_print_eq()

```

The above example allows for things like a simple api to be created to allow
users to run optimizations that have been designed by disciplinairy engineers,
but also brings forth a few questions.

1. Are there any core issues with using OpenMDAO like this?
2. How can the user functions like `u_plot()` and `u_print_eq()` be created? (by
the coder of the object, not the dev team)

In terms of the first question, my team and I have been working on a fairly
large project over the past 2 years that uses OpenMDAO (albeit with a few
workarounds) that works quite well. Due to it's industrial nature I can't post
it publically but I'd be happy to discuss portions it on a one on one basis and 
I am very open to feedback on potential issues that may arise.

In terms of the second question, I have 3 methods to propose, 2 that require
enhancements to OpenMDAO (hence the POEM) and one that does not which can 
be used in the event that the PEOM is politely rejected.

## Implentation 1 - Seperation of get_val from dependancy on the Problem Object
Any user function with the intent to display results will need a manner of
retrieving those results. The built-in OpenMDAO way of retrieving results in 
through the get_val() method which appears to be available to the Problem object
as well as to components and groups. The advantage of using it at the component/
group level is that local inputs/output data can be retrieved using the local 
naming so that the retrieval is independact of the model structure above it (i.e
get_val can be used the same way locally regardess if `Parabola` is being run on
it's own or part of larger systems)

This would give the following implentation of `Parabola.u_print_eq()`

```python
    def u_print_eq(self):
        a = self.get_val('a', units='mm')
        print(f'Optimized Inner Parabola: y = (x-{a})**2 + 4')
```

With the current version (3.8) of OpenMDAO, the following code will break the 
above implementation

```python
import gc # Garbage collection

p = Parabola()
p.set_x(3)
p.u_run_opt()
gc.collect() # To ensure the problem object in u_run_opt is removed from memory
p.u_print_eq()
```

A proposed workaround (which works in some cases) is simply to stash the problem
object somewhere (such as making it an attribute of the component). This was 
proposed by Justin Grey when this was submitted as an Issue.

The issue with this is that the component becomes no longer picklable once the 
problem has run due to the use of weakrefs. Pickling (or serializing) the object
can be useful for a variety of reasons such as saving the object or when one is 
working on the GUI side passing the object between threads or processes.
Serialization could still be accomplished using a heavier serializer such as 
Dill, but this add a decent amount of overhead and processes time. Additioanlly, 
the problem in general adds significant size to the object given that it is only
being used for local data retrieval. We can imagine a problem where many of
these obejct are being used and persisting many Problems in memory may not be
desirable.

## Implentation 2 - Creating of a post_run() function
A second implementation to allow user interfacing with the data (among other 
things) could be the creation of a `post_run()` function as part of the core
OpenMDAO callstack. This would be a method that gets run in the same way as the 
compute function does when one uses `run_model()` however it gets run after 
the driver has completed. This would allow the object to do whatever is needed 
with to the OpenMDAO data while the problem still persists and more generally 
speaking, do any local cleanup or computations that don't need to be included in
the `compute` method.

We can imagine a `Parabola.post_run()` function that may look as follows

```python
    def post_run(self, inputs, outputs):
        self.y = self.get_val('y', units='mm')
        self.a = self.get_val('a', units='mm')
```

And then the `Parabola.u_print_eq()` can simply reference the class attributes
`a` and `y`.

This method could give users a variety of flexibility when it comes to how they
choose to interface with the results of an optimization.

## Implementation 3 - No Changes to OpenMDAO
As an alterante to the above implementations, the class attribute assignment 
could actually just occur in the regular compute function like follows.

```python
    def compute(self, inputs, outputs):
        x = inputs['x']
        a = inputs['a']
        y = (x-a)**2 + 4
        outputs['y'] = y
        self.x = x
        self.y = y
```

These variables would then just be left to the user as they appear in the final 
iteration. This can be problematic for a variety of reason namely that if
complex stepping is used, it's possible that these could end up being complex 
numbers and moreso this really just doesn't seem like the intended use of the 
`compute()` function.

## Pull Requests
I have not yet made pull requests, although I have demoed modifications to allow
each of these implentation to work. I wouldn't be surpised if my modification
may break other features, so I would like to wait for some community/dev
feedback before spending too much time perfecting them.

As a brief summary of my initial modidification:

Implentation 1 involves modification to the 
`System.get_val()` method so that when `from_src` is false, the weakref to the 
problem from the line 
`conns = self._problem_meta['model_ref']()._conn_global_abs_in2out`
is never called.

EDIT: Implementation 1 now has the OpenMDAO pull request #2005

Implementation 2 involves the creation of new System method called 
`run_post_run()` (or something that sounds better than that) which is
essentially a deep duplicate of `System.run_solve_nonlinear()` and the methods
it calls where at the end, the new `post_run()` is called instead of `compute()`

NOTE: We're leaving this part of the implementation out.  We feel it would be better to
have such access be a user-created post-processing function for a specific use-case
rather than modifying the API.

