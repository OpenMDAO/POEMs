POEM ID: 095
Title: Support user/developer defined callback functions
authors: A-CGray (Alasdair Christison Gray), eytanadler (Eytan Adler), hajdik (Hannah Hajdik)
Competing POEMs:
Related POEMs:
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

Commonly, a user will want to perform an action once per evaluation of their model.
For example, if a model contains a component that wraps an external solver (e.g CFD), the user may want to make a call to that solver to write out a solution file after each evaluation of the model.

Currently the only way to implement this behaviour is to do it inside one of the required methods of a component/group (e.g `compute`, `solve_nonlinear` etc)
However, these implementations almost always require some assumptions about the way in which that component/group will be called by OpenMDAO, and so are not very robust.
For example, in the case of an implicit component that wraps a CFD solver, writing the solution file inside `solve_nonlinear` would work in some cases:

```python
class CFDSolverComponent(om.ImplicitComponent):

    .
    .
    .

    def solve_nonlinear(self, inputs, outputs): # This may be called once, none, or multiple times per model evaluation
        # Set inputs to the CFD solver
        self.CFDSolver.setNodeCoordinates(inputs['nodeCoordinates'])
        self.CFDSolver.setState(outputs['flowState'])
        # Call the CFD solver and put the solution in the outputs
        self.CFDSolver.solve()
        outputs['flowState'] = self.CFDSolver.getState()
        # Write the solution file
        self.CFDSolver.writeSolution()
```

However, if the component is used inside an NLBGS cycle then the solution file would be written multiple times, and if used inside a Newton solver then the solution file would not be written at all.
There are ways around this specific example, but in general, implementing these kinds of capability always involve some fairly hacky code.

## Proposed solution

We propose that OpenMDAO add support for callback functions written either by users or component developers.
These callback functions would be called at specific points in the execution of the model, and would be able to access the model and its components in order to perform some action.

There are multiple levels at which these callbacks could be defined:

### Problem level callbacks

Probably the simplest implementation. The user defines a callback function for their problem and OpenMDAO calls it at the end of `run_model`.
The problem itself would be passed as an input to the callback function, giving the user full access to any of the problem's attributes.

```python
def myGroup(om.Group):
    .
    .
    .

    def setup(self):
        self.add_subsystem('CFDSolver', CFDSolverComponent())

    .
    .
    .

def problem_callback(problem): # This will be called at the end of run_model
    problem.model.CFDSolver.writeSolution()

prob = om.Problem(model=myGroup())
prob.set_callback(problem_callback)
```

### Driver level callbacks

The user defines a callback function that is called by the driver at various points in its execution.
Which points these are would be driver specific, for example in a DOE driver the callback might be called after each model evaluation, whereas in an optimization driver it might be called after each model evaluation and after each gradient evaluation.
In the case where a driver can call a callback for several reasons, OpenMDAO could either require separate callback functions for each reason, or it could pass an argument to the callback function that indicates the reason for the call.
An example of where this may be useful is if the user wanted to only write solution files at the end of each major iteration of an optimization, instead of at the end of every model evaluation.

```python
def myGroup(om.Group):
    .
    .
    .

    def setup(self):
        self.add_subsystem('CFDSolver', CFDSolverComponent())

    .
    .
    .

def problem_callback(problem, event):
    if event == 'major_iteration':
        problem.model.CFDSolver.writeSolution()

prob = om.Problem(model=myGroup())
prob.driver = om.pyOptSparseDriver()
prob.driver.set_callback(problem_callback)
```

### Component/group level callbacks

These callback functions could be defined within a component or group, in a similar manner to optional methods like `solve_nonlinear`.
The advantage of this approach is that component developers can define callbacks to do things that the user commonly wants to do, so the user doesn't have to implement their own higher level callback to do them every time they use the component.
For example, the developers of the `CFDSolverComponent` could define a callback that writes the solution file so the user doesn't have to:

```python
class CFDSolverComponent(om.ImplicitComponent):

    .
    .
    .

    def solve_nonlinear(self, inputs, outputs): # This may be called once, none, or multiple times per model evaluation
        # Set inputs to the CFD solver
        self.CFDSolver.setNodeCoordinates(inputs['nodeCoordinates'])
        self.CFDSolver.setState(outputs['flowState'])
        # Call the CFD solver and put the solution in the outputs
        self.CFDSolver.solve()
        outputs['flowState'] = self.CFDSolver.getState()

    def post_evaluation_callback(self, inputs, outputs): # This is guaranteed to be called at the end of each model evaluation
        self.CFDSolver.writeSolution()
```

## Similarity with recorders

Maybe this can be integrated with the recorder system since it follows a similar principle of being applicable at different levels of the model hierarchy, and the recorder is called after the execution of the thing it is attached to.
The idea would be to be able to attach a callback to a recorder, and then the recorder would call the callback each time it records something.
