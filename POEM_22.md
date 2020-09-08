POEM ID:   022  
Title:  POEM 22:Shape inputs/outputs by connection or copy from another component variable   
Authors: joanibal (Josh Anibal)   
Competing POEMs: N/A  
Related POEMs: N/A
Associated implementation PR: None (yet)

Status:

- [] Active
- [x] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


# Motivation

Modularity is a critical aspect of OpenMDAO since it is designed to facilitate the use of discipline based components in many different multi-disciplinary models. 
In order to be modular often a component is required to have inputs and outputs of variable shape.
For example, components of a PDE based analysis must work with variables that have a shape defined by a mesh file.


Passing shape as an option 
--------------------------
One method of making components modular is to pass an additional variable as an option which specifies the shape of the input vectors. 
To utilize this method, at the time the component is created the shape variable argument must be passed. 
This solution has worked well for many applications and is generally the way to do things in OpenMDAO as shown by the many modular components included with OpenMDAO that use this method (DotProductComp for example). 

However this method does not work if the inputs and outputs shapes are unknown when the component is created. 
Consider the case where during the setup a mesh is read to create the inputs and outputs of a component.
This could not happen during the initialization of the object if the method used to read the mesh requires the component's MPI comm, which is typically the case in practice.
In this case, the shape of the mesh can not be passed as an argument to other subsystems as they are create because the  they are created before any of the system setup methods are run.


Builders
--------
One method to get around this issue is to use a "builder" (see the MPHYS project).
The builder object can read in the mesh and pass shape data to each of the components as they are created. 
Builders can be passed as an arguments to other builders to share shape information between subsytems (in MPHYS this is used by the transfer components).

However, this method greatly increases the complexity of the code and reduces modularity. 
For each new model in which the components are used, a new builder must be made or an existing builder must be generalized (increasing complexity). 
Additionally, Now instead of writing components, users must write custom classes which create components. 
This is a different design pattern than what is used for low fidelity simulations and is likely to cause confusion for OpenMDAO users when they first try to incorporate a high fidelity model in OpenMDAO.


Add variables during configure
------------------------------
A third method that exists is to add add the inputs and outputs of a unknown shape to the components during the configure method of a group.
Because the configure method is called after the setup, the inputs and outputs can be added with correct shape. 

The major draw back of this method is that the information about these inputs and outputs exists only at the group level, which sacrifices a great deal of modularity and clarity. 
Now the components do not contain enough information to be used in a model by themselves.
The information about their inputs and output must be added to the model configuration or they must be used in an existing group which supplies the remaining information in its configure.
Because the inputs and outputs must be restated for every group or model the component is used in, modification to the inputs/outputs, such as adding a new variables or changing variable names, units, and or description must be be repeated for every group or model the component is used in. 
An Additional source of frustration is that the description of the input/output included in their definition now exists outside of the component definition. 



# Description

The solution I propose to create modular components of variable shape is to allow inputs and outputs to get their shape information from their connections or 
by copying the infomation of another variable in the componet. 

shape by connection
---------
When two variables are connected their shapes must match. 
Therefore, connecting a variable with a known shape to one of an unknown shape can be used to specify the unknown shape. 
By adding a keyword to the input or output definition we can specify that the shape of the input or output should be determined in this way
This method of specifying inputs or outputs of variable shape will make it easy to create components to represent mathematic functions that 
act on vectors of arbitrary size such as norms, integrators, weighted averages, inner products, etc. 
Some examples of how this idea could be implemented in practice are shown below. 



```python
class VecSum(om.ExplicitComponent):
    """
    Calculates the sum of the elements of the input vector x
    """

    def setup(self):


        # the shape of the input is not known when the 
        # component is defined
        self.add_input('x', shape_by_connection=True)
        self.add_output('sum', shape=1)

    .
    .
    .
```


```python
class SurfaceIntegration(om.ExplicitComponent):
    """
    Calculates the sum of the elements of the input vector x
    """

    def setup(self):


        # the shape of the inputs is not known when the 
        # component is defined
        self.add_input('X', shape_by_connection=True, desc='Surface nodal grid points', units='m')
        self.add_input('P', shape_by_connection=True, desc='Pressure at the cell center', units='Pa')


        self.add_output('Forces', shape=3, desc='resultant force', units='N')
    .
    .
    .
```




Copy Shape 
---------
The shape of one variable is often the same as another. 
When used in conjuction with the shape_by_connection idea, this method can be used to pass shape information through the component. 






```python
class RotateMesh(om.ExplicitComponent):
    """
    Rotates a cloud of points ('X') around an axis (axis) by an angle (ang) to create a new set of points ('Xrot').
    """

    def setup(self):

        self.add_input('X', shape_by_conn=True, desc='mesh nodes')
        self.add_input('axis', shape=3, desc='axis of rotation')
        self.add_input('ang', shape=1, desc='angle of rotation', units='rad')


        # the shape of this output is the same as X
        self.add_output('Xrot', copy_shape='X, shape_depends_on=['X'])

    .
    .
    .
```


# Implementation
See the [PR associated](https://github.com/OpenMDAO/OpenMDAO/pull/1646) with this POEM for my idea about how this idea could be implemented. 







