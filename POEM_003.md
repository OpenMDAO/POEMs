POEM ID: 003  
Title: Adding a pre_setup method to create objects and communicators  
Author: anilyil (Anil Yildirim)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status: 

 - [x] Active
 - [ ] Requesting decision
 - [ ] Accepted
 - [ ] Rejected


Problem statement
=================

OpenMDAO problems contain a method called `setup`, which is called by the user after the user specifies all components and connections.
No fundamental changes to the components can be done after this method is called; in particular, sizes of the intputs and outputs for any component cannot be changed.
Furthermore, the communicators are not created until `setup` is called, therefore users cannot initialize supplementary Python objects that require access to the communicator.

Frequently, these objects that require the communicator needs to be initialized to determine the input and output sizes for their components, effectively creating a circular dependency.
This factor makes it difficult to integrate complied analysis codes in OpenMDAO components in a modular way.
This problem is currently avoided by ad hoc implementations, where the Python objects pass information in a layer hidden from OpenMDAO, which is not ideal and limits the flexibility of the framework.




Suggested solution
==================

We suggest adding a `pre_setup` method to the `Problem` class in OpenMDAO.
This method will:

1. Create the communicators,
2. traverse down the model hierarchy and call the `pre_setup` method on all components, and
3. traverse up the model hierarchy and call the `pre_configure` method on all components.

After `pre_setup` is called, the user will still be able to make new connections in the model, and define new input and outputs for any component.
Furthermore, the user will be able to access the communicators, and the objects created for each component as attributes of the OpenMDAO `problem` instance.
The model hierarchy can be fixed after this step.
We do not have any strict requirements on any of the method names. The 3rd step is open to discussion, however, our main suggestion is adding step 2.

Our goal with this approach is to define a way to initialize the communicators and Python objects, before any of the input and output vector sizes are frozen.
This enables compiled analysis codes that require access to the communicators to be initialized and saved as attributes of their OpenMDAO components that contain them.

Because the user can still add new inputs and outputs, and make new connections after this stage, the user can access the created Python objects and communicate across components at the top level script.
This enables mimicking the Python-based optimization frameworks such as the MACH framework developed by the MDO Lab.

Example script
==============

The pseudo-code for an example optimization script is listed below:


```python
from openmdao.api import Problem
from MACH-Aero import DVGeometryComp, ADflowComp

# initialize the OpenMDAO problem
p = Problem()

# add geometry component
p.model.add_subsystem('geometry', DVGeometryComp())

# add solver component
p.model.add_subsystem('solver', ADflowComp())

# call pre_setup
# all communicators and components are initialized with this method
p.pre_setup()

# add geometry design variables
# this method also adds 'twist' as an output of the comp
p.model.geometry.addDVGeoGlobal('twist')

# get surface coordinates from solver
surfaceCoords = p.model.solver.getSurfaceCoordinates()

# add them as an output to the geometry component
# this method also adds 'cfd_surface' as an output of the comp
p.model.geometry.addPointSet(surfaceCoords, 'cfd_surface')

# connect surface output from geometry to the CFD
p.model.connect('geometry.cfd_surface', 'solver.surfaceCoordinates')

# call setup
p.setup()

# run
p.run_model()
```

In this example, we add two components to the model; one for manipulating the geometry, and a CFD solver.
The geometry component takes in geometric design variables, and outputs the updated surface definition of the CFD problem.
However, until the CFD solver is initialized, we cannot access the size and values of the output for the surface coordinates.

The `pre_setup` method enables us to initialize the geometry and solver components before the actual `setup` call, and therefore we can access the surface coordinates that define the CFD problem and add these as an output to the geometry component.

In this example code, we kept every call in the actual run script for transparency.
However, we can hide the generic connection calls (e.g. `getSurfaceCoordinates`, `addPointSet`) from the user by using utility functions, since these connections can be defined as standard interfaces between the geometry and solver components, and will remain the same across problems.
As a result, we can only keep the problem specific calls in the actual run script, like adding design variables.

Contributors
============

This proposal is made by the MDO Lab at University of Michigan.
People who are actively involved in the proposal (in no particular order):
Anil Yildirim, Joshua L. Anibal, Benjamin J. Brelje, Nicolas P. Bons, Charles A. Mader, Joaquim R.R.A. Martins

