POEM ID:   022  
Title:  Shape inputs/outputs by connection or function.   
Authors: joanibal (Josh Anibal)   
Competing POEMs: N/A  
Related POEMs: N/A
Associated implementation PR: None (yet)

Status:

- [x] Active
- [ ] Requesting decision
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
Builders can be passed as an arguments to other builders to share shape information between subsytems (in MPHYS this is used by the transfer components)

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


<!-- The final method I'm a aware of is to 
Move code to read mesh file into initialize 

Finally, 
need mpi communicators 
- can't create input/outputs in init
- breaks trend of using the initialize method to declare options
- shape information stored using attr or method which exist outside the API 
- mesh readers must use the same attr/method names to be swapable 
<!-- - all information is saved becuase it not known yet what information is needed  -->

# Description

The solution I propose to create modular components of variable shape is to allow inputs and outputs to get their shape information from their connections or 
by a function. 

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




shape by function 
---------
The shape of one variable often depends on the shape of other. 
To leverage this idea in OpenMDAO, we can use the relationship between variable shapes as a method of declaring shape in the definition of inputs and outputs. 
However, to figure out what order the relationships should be resolved OpenMDAO must know what variable shapes this variable's shape depends on. 
This can be done by passing another keyword argument to the input and output definition that explicitly defines the dependence. 
Using this method we can easily create components with act on vectors of arbitrary shape and have a relationship between variables based on that arbitrary shape. 
Such components could include mesh refinement, rotations, solution interpolation, matrix decompositions. 



```python
class Interpolate(om.ExplicitComponent):
    """
    interpolates the coarse solution 'u_coarse' to the fine solution 'u_fine',
    which is twice as dense along each dimension.
    """

    def setup(self):

        self.add_input('u_coarse', shape_by_connection=True)

        def my_shape_func(var_meta):
            """
             function run to determine the shape of the variable

             parameters
             ----------
             var_meta: dictionary of meta data objects for each of the variables
                       on this component
            
             Returns
             ----------
             shape: tuple
                 the shape of the variable
            """
            shape = var_meta['u_coarse'].shape*2

            return (shape)

        # the shape of this output is related by the function to the shape of the variables defined
        # in shape_depends on 
        self.add_output('u_fine', shape_function=my_shape_func, shape_depends_on=['u_coarse'])

    .
    .
    .
```



```python
class RotateMesh(om.ExplicitComponent):
    """
    Rotates a cloud of points ('X') around an axis (axis) by an angle (ang) to create a new set of points ('Xrot').
    """

    def setup(self):

        self.add_input('X', shape_by_connection=True, desc='mesh nodes')
        self.add_input('axis', shape=3, desc='axis of rotation')
        self.add_input('ang', shape=1, desc='angle of rotation', units='rad')



        def my_shape_func(var_meta):
            return (var_meta['X'].shape)

        # the shape of this output is related by the function to the shape of the variables defined
        # in shape_depends on 
        self.add_output('Xrot', shape_function=my_shape_func, shape_depends_on=['X'])

    .
    .
    .
```


```python
class OuterProduct(om.ExplicitComponent):
    """
    computes the outer product of the two input vectors 
    """

    def setup(self):

        self.add_input('vec_1', shape_by_connection=True)
        self.add_input('vec_1', shape_by_connection=True)



        def get_mat_shape(var_meta):
            return (var_meta['vec_1'], var_meta['vec_2'])

        # the shape of this output is related by the function to the shape of the variables defined
        # in shape_depends on 
        self.add_output('mat', shape_function=get_mat_shape, shape_depends_on=['vec_1', 'vec_2'])

    .
    .
    .
```


# Implementation

There is no PR associated with this POEM for two reason. 
One, want to see if the dev team though it was a good idea before investing more time into it.
Two, I expect that implementing this feature would require detailed knowledge of OpenMDAO to do right. 
However, I have looked at the code used to setup a model and come up with an idea of how it could work.

After configure is called on all components, preform the following steps 
- Create a global decency graph for the model using the given shape dependencies
    - Variables using shaped_by_connection have a dependency on the shaped variable they are connected to.
- Check that the dependency graph forms a tree, if it doesn't there is a circular dependency
- move up the dependency tree levels to find the shapes for all the inputs/outputs  

Then continue with normal connection shape checking and final setup 

An error should be raised if
- a shape_by_connection component is not connected 
- there is a circular decency in a group dependency graph 







