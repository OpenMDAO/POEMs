POEM ID: 003  
Title: Allowing addition if I/O during Configure
Author: anilyil (Anil Yildirim); justinsgray (Justin Gray); robfalck (Rob Falck)
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [https://github.com/OpenMDAO/OpenMDAO/pull/1140, ]

Status: 

 - [ ] Active
 - [ ] Requesting decision
 - [ ] Accepted
 - [ ] Rejected
 - [x] Integrated


Problem statement
=================

OpenMDAO components and groups utilize a `setup` method to get themselves properly built up and ready for execution. 
By the time a particular `setup` method that component or group already has access to its comm object. 
For groups, though they have their own comm, any children that they create during setup do not get their child-comms within that groups setup method. 
This is because the `setup` method recurses down the model tree, building it as it goes. 

This works fine as all children in a group can be created using only information already known to that group, but do not require any information from their siblings in the hierarchy. 
That is not to say that there can't be connections between children, but rather that no child needs information that any sibling would create in its `setup` --- which has not yet been called while still inside the parent group's `setup`. 

In cases where one child needs information from a sibling's `setup` call, then the current timing of the setup-stack is not sufficient. 
One example of when this might occur is when dealing with a CFD solver that requires access to its comm to load its mesh and figure out the sizes of its state vector on each process. 
Until the component has the comm, the I/O can't be created. Many things downstream of the CFD component might need to know the size of the state vector, or its distribution across the processors. 
That kind of setup process can't be accommodated with the current top-down setup method in group. 

So there needs to be a way for children of groups to do key setup tasks such as add I/O and issue connections, after the full hierarchy has been constructed and all groups/components all the way down have their comms. 
What is needed is a method that can be defined on groups which gets called in a bottoms-up manner, after the full hierarchy has been built. 
Groups already have a `configure` method, which is called with precisely this timing, but as of V2.9.1 you could only make changes to solver setups and issue connections. 
You could not make changes to the I/O configuration of components within the `configure` method. 

This POEM proposes modifying OpenMDAO so that I/O can be created in the `configure` method, to enable this use case. 
Along with the change in functionality, several other smaller changes also need to be included. 
Users must also be able to query children of a group for information about I/O status from within the `configure` method. 


Proposed API Changes
====================

1.  Group Promotes Method

The suggested signature of the Group `promotes` method is

```
def promotes(subsys_name, any=None, inputs=None, outputs=None, 
             src_indices=None, flat_src_indices=False)

Parameters
----------
subsystem_path : str
    The name of the child subsystem whose inputs/outputs are being promoted.
any : Sequence of str or tuple
    A Sequence of variable names (or tuples) to be promoted, regardless 
    of if they are inputs or outputs. This is equivalent to the items 
    passed via the `promotes=` argument to add_subsystem.  If given as a
    tuple, we use the "promote as" standard of ('real name', 'promoted name')*[]: 
inputs : Sequence of str or tuple
    A Sequence of input names (or tuples) to be promoted. Tuples are
    used for the "promote as" capability.
outputs : Sequence of str or tuple
    A Sequence of output names (or tuples) to be promoted. Tuples are
    used for the "promote as" capability.
src_indices : int or list of ints or tuple of ints or int ndarray or Iterable or None
            This argument applies only to promoted inputs. 
            The global indices of the source variable to transfer data from.
            A value of None implies this input depends on all entries of source.
            Default is None. The shapes of the target and src_indices must match,
            and form of the entries within is determined by the value of 'flat_src_indices'.
flat_src_indices : bool
            This argument applies only to promoted inputs. 
            If True, each entry of src_indices is assumed to be an index into the
            flattened source.  Otherwise each entry must be a tuple or list of size equal
            to the number of dimensions of the source.
```

Promotes can only be used to promote directly from the children of the current
group (one step, no more).  Promoting things up a chain can be accomplished
by multiple calls.

The `src_indices` and `flat_src_indices` arguments should apply only to the variables 
specified in the `inputs` argument.  
If a user wants to give different `src_indices` for different variables, 
they can do so via separate calls to promotes. 

Users can potentially define `src_indices` in both the `add_input` call on the component and in the `promotes` call in the group. 
In the event that there is a conflict between these specifications the following precedence should be followed: 
* If the user specifies `src_indices` and/or `flat_src_indices` only at the group level, 
then the the group level superceeds the component level and all inputs will use the group specification. 
* If the user specifies `src_indices` and/or `flat_src_indices` at both the group level and also at the component level, 
then the two specifications must match (in both shape and values) otherwise it is an error. 
* If the user specifies `src_indices` and/or `flat_src_indices` at only the component level, but not at the group level then each input can have its own `src_indices` which will be respected. 
This behavior matches what already happens in V3.0 when `src_indices` are specified at the component level and then the input is promoted. 

2.  Disable the use of `add_subsystem` during the configure portion of the setup stack.

Currently adding subsystems during the configure portion of the stack does not raise, but  
it has undefined behavior that doesn't accomplish what the user expects.  
Calling add_subsystem once configure has begun should explicitly raise an exception.


Example script
==============

```python
import numpy as np
import openmdao.api as om

class FlightDataComp(om.ExplicitComponent):
    """
    Simulate data generated by an external source/code
    """
    def setup(self):
        # number of points not known till after setup is called
        n = 3

        self.add_input('scaler', 4)

        # The vector represents forces at n time points (rows) in 2 dimensional plane (cols)
        self.add_output(name='thrust', shape=(n, 2), units='kN')
        self.add_output(name='drag', shape=(n, 2), units='kN')
        self.add_output(name='lift', shape=(n, 2), units='kN')
        self.add_output(name='weight', shape=(n, 2), units='kN')

    def configure(self, inputs, outputs):
        outputs['thrust'][:, 0] = scaler*np.array([500, 600, 700])
        outputs['drag'][:, 0]  = scaler*np.array([400, 400, 400])
        outputs['weight'][:, 1] = scaler*np.array([1000, 1001, 1002])
        outputs['lift'][:, 1]  = scaler*np.array([1000, 1000, 1000])


class ForceModel(om.Group):
    def setup(self):
        self.add_subsystem('flightdatacomp', FlightDataComp(),
                           promotes_outputs=['thrust', 'drag', 'lift', 'weight'])

        self.add_subsystem('totalforcecomp', om.AddSubtractComp())

    def configure(self):
        # Some models that require self-interrogation need to be able to add
        # I/O in components from the configure method of their containing groups.
        # In this case, we can only determine the 'vec_size' for totalforcecomp
        # after flightdatacomp has been setup.

        flight_data = dict(self.flightdatacomp.list_outputs(shape=True, out_stream=None))
        data_shape = flight_data['thrust']['shape']

        self.totalforcecomp.add_equation('total_force',
                                         input_names=['thrust', 'drag', 'lift', 'weight'],
                                         vec_size=data_shape[0], length=data_shape[1],
                                         scaling_factors=[1, -1, 1, -1], units='kN')

        p.model.connect('thrust', 'totalforcecomp.thrust')
        p.model.connect('drag', 'totalforcecomp.drag')
        p.model.connect('lift', 'totalforcecomp.lift')
        p.model.connect('weight', 'totalforcecomp.weight')


p = om.Problem(model=ForceModel())
p.setup()
p.run_model()

print(p.get_val('totalforcecomp.total_force', units='kN'))
```

Contributors
============

This proposal is originally made by the MDO Lab at University of Michigan.
People who are actively involved in the proposal (in no particular order):
Anil Yildirim, Joshua L. Anibal, Benjamin J. Brelje, Nicolas P. Bons, Charles A. Mader, Joaquim R.R.A. Martins

Contributions were also made by the OpenMDAO Dev team. 

