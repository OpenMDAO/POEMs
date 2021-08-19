POEM ID: 046   
Title: Definition of serial and distributed variables   
authors: [justinsgray, naylor-b, joanibal, anilyildirim, kejacobson]    
Competing POEMs: N/A    
Related POEMs: 022, 044   
Associated implementation PR: #2013

#  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

# Motivation

As of OpenMDAO 3.8.0 there is significant confusion surrounding connections between serial and distributed variables, what happens when you do or do not specify `src_indices`, and what happens if you use `shape_by_conn` in these mixed serial/distributed situations. 

The main purpose of this POEM is to provide clarity to this situation by means of a clear, concise, and self-consistent explanation. 
Some modest changes to APIs are proposed because they help unify what are currently corner cases under one simpler overall philosophy. 


# Overview of Serial and Distributed Computation in OpenMDAO

Serial vs distributed labels can potentially come into play in three contexts: 
1) Components 
2) Variables
3) Connections

## Components are not classified as serial/distributed
OpenMDAO makes no assumptions about what kind of calculations are done inside the `compute` method of your components. 
**There is no fundamental difference between a serial component and a distributed component**. 
Components are always duplicated across all the processors alloted to their comm when running under MPI. 

Consider this trivial illustrative example:

```python
import openmdao.api as om 

class TestComp(om.ExplicitComponent): 

    def setup(self): 
        self.add_input('foo')
        self.add_output('bar')

        print('rank:', self.comm.rank, "comm size: ", self.comm.size)

p = om.Problem()

p.model.add_subsystem('test_comp', TestComp())

p.setup()

p.run_model()
``` 

When run with `mpiexec -n 3 python example.py` we get 3 copies of `TestComp`, one on each processor.
```
rank: 0 comm size:  3
rank: 1 comm size:  3
rank: 2 comm size:  3
```

An important side note is that while a component is always copied across its entire comm, 
OpenMDAO can split a comm within a model so that it is absolutely possible that a component is only setup on a sub-set of the total processors given to a model. 
Processor allocation is a different topic though, and for the purposes of POEM 046, we will assume that we are working with a simple single comm model. 

## What it means for a variable to be serial or distributed in OpenMDAO

A `serial` variable has the same size and the same value across all the processors it is allocated on. 
A `distributed` variable has a potentially varying size on each processor --- including possibly 0 on some processors --- and a no assertions about the various values are made. 
The sizes are "potentially varying" because its possible to have a distributed variable with the same size on every processor, but this would just be incidental. 

Note that even for a serial variable, there are still multiple copies of it on different processors. 
It is just that we know they are always the same size and value on all processors. 
The size guarantee is easily enforced during model setup. 
The value guarantee is a little more tricky because there are two ways to achieve it: 
- Perform all calculations on a single processor and then broadcast the result out to all others 
- Duplicate the calculations on all processors and use the locally computed values (which are the same by definition because they did the same computations)

OpenMDAO uses the duplicate calculation approach for serial components, 
because this results in the least amount of parallel communication and has other advantages in parallel computation of reverse-mode derivatives in some cases. 

## Places where serial/distributed labels impact OpenMDAO functionality

There are a few places where serial/distributed matters: 
- For serial variables `src_indices` are specified based on their local size, and internally OpenMDAO will offset the indices to ensure that you get the data from your local processes. 
- For serial variables OpenMDAO can check for constant size across processors
- When allocating memory for partial derivatives, OpenMDAO needs to know the if variable data on different processors are duplicates (serial variables) or independent values (distributed) so it gets the right size for the Jacobian. 
- When computing total derivatives the framework needs to know if values are serial or distributed to determine the correct sizes for total derivatives, and also whether to gather/reduce values from different processors.

To understand the relationship between serial/distributed labels and partial and total Jacobian size consider this example (coded using the new proposed API from this POEM): 

```python
import numpy as np

import openmdao.api as om 

class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo')  # foo is scalar

        DISTRIB = True
        if DISTRIB: 
            self.out_size = self.comm.rank+1
        else: 
            self.out_size = 3
        self.add_output('bar', shape=self.out_size, distributed=DISTRIB)

        self.declare_partials('bar', 'foo')

    def compute(self, inputs, outputs): 

        outputs['bar'] = 2*np.ones(self.out_size)*inputs['foo']

    def compute_partials(self, inputs, J): 
        J['bar', 'foo'] = 2*np.ones(self.out_size).reshape((self.out_size,1))

p = om.Problem()

# NOTE: no ivc needed because the input is serial
p.model.add_subsystem('test_comp', TestComp(), promotes=['*'])

p.setup()

p.run_model()

J = p.compute_totals(of='bar', wrt='foo')

if p.model.comm.rank == 0: 
    print(J)
```
When run with via `mpiexec -n 3 python <file_name>.py`,
with `DISTRIB = True` you would see the total derivative of `foo` with respect to `bar` is a size (6,1) array: `[[2],[2],[2],[2],[2],[2]]`.
The length of the output here is set by the sum of the sizes across the 3 processors: 1+2+3=6. 
Each local partial derivative Jacobian will be of size (1,1), (2,1), and (3,1) respectively. 
Each local partial derivative Jacobian represent a portion of the global partial derivative Jacobian across all 3 processes. 

With `DISTRIB = False` you would see the total derivative of `foo` with respect to `bar` is a size (3,1) array: `[[2],[2],[2]]`.
The local partial derivative Jacobian will be of size (3,1) on every processor. 
In this case, the local partial derivative Jacobian is the same as the global partial derivative Jacobian.


# Proposed API for controlling how serial components are executed on multiple processors

As shown in the examples above, OpenMDAO duplicates all components across every process in their comm. 
For serial components, this means that by default all calculations are duplicated across the various processes. 
This design works well because it allows local data transfers (vs requiring a broadcast from the root proc) which avoids MPI communication overhead. 
It also has advantages when computing derivatives, because the multiple copies can be used to improve parallelism in both forward and reverse mode calculations. 

However, there are some cases where duplication of the serial calculations is not desirable. 
Perhaps there is a numerically unstable matrix inverse that would get slightly different results on different processes, which could cause problems. 
Or there may be some file I/O involved which should not be done by more than one process. 
In these cases, the desired behavior is for a serial component to do all its calculations on the root process, and then broadcast the results out to all the copies. 
If you need/want the broadcast approach, 
you can manually create it by adding an internal broadcast to the compute method of your component: 

```python 
def compute(self, inputs, outputs):
        bar = 0
        if self.comm.rank == 0:
            bar = inputs['foo'] + 1
        bar = self.comm.bcast(bar, root=0)
        outputs['bar'] = bar
``` 

This would give the desired behavior, but it requires modifying a component's compute method. 
Requiring modifications of serial components in order to run them as part of a distributed model is undesirable. 
To avoid this, components will be given a new option that controls their serial behavior: `run_root_only`. 

If `self.options['run_root_only'] = True` then a component will internally restrict its own compute method to run only on the root process, and will broadcast all its outputs. 
This same behavior will also be applied to any derivative methods (`linearize`, `compute_partials`, `apply_linear`, `compute_jac_vec_product`), which will only get run on the root process and their computed results broadcast out to all the other processes. 
In the case of any reverse mode derivatives, OpenMDAO will internally do a reduce to the root processor to capture any derivative information that was being propagated backwards on other processors. 

When `self.options['run_root_only'] = True`, all inputs and outputs of the component MUST be `serial`. 
The variables can either be left unlabeled and will be assumed `serial` or they can be explicitly labeled as such. 
If any component variables are labeled as `distributed`, an error will be raised during setup. 

One other detail that is worth noting is that the `run_root_only` option will not interact cleanly with some of the parallel derivative functionality in OpenMDAO. 
[Parallel-FD](http://openmdao.org/twodocs/versions/3.8.0/features/core_features/working_with_derivatives/parallel_fd.html), and [parallel-coloring for multi point problems](http://openmdao.org/twodocs/versions/3.8.0/features/core_features/working_with_derivatives/parallel_derivs.html) will both not work in combination with this option. 
During setup, if either of these features is mixed with a component that has this option turned on an error will be raised. 


# Proposed API for labeling serial/distributed variables

A `distributed` argument will be added to the `add_input` and `add_output` methods on components. 
The default will be `False`. 
Users are required to set `distributed=True` for any variable they want to be treated as distributed. 

one serial input (size 1 on all procs, value same on all procs), 
one distributed output (size rank+1 on each proc).
```python
class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo')
        self.add_output('bar', shape=self.comm.rank+1, distributed=True)
```

one distributed input (size 1 on all procs), 
one distributed output (size 1 on all proc).
```python
class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo', distributed=True)
        self.add_output('bar', distributed=True)
```

one distributed input (size 1 on all procs), 
one serial output (size 10 on all procs, value same on all procs).
```python
class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo', distributed=True)
        self.add_output('bar', shape=(10,))
```

This API will allow components to have mixtures of serial and distributed variables. 
For any serial variables, 
OpenMDAO will be able to check for size-consistency across processors during setup.

Although value-consistency is in theory a requirement for serial variables in practice it will be far too expensive to enforce this. 
Hence it will be assumed, but not enforced. 

# Connections between serial and distributed variables

In general there are multiple ways to handle data connections when working with multiple processors. 

Serial/distributed labels are a property of the variables, 
which are themselves attached to components. 
However, the transfer of data from one component to another is governed by `connect` and `promotes` methods at the group level. 
When working with multiple processors, you have to consider not just which two variables are connected but also what processor the data is coming from. 
This is all controlled via the `src_indices` that are given to `connect` or `promote` methods on `Group`. 

One of primary contributions of POEM_046 is to provide a simple and self consistent default assumption for `src_indices` in the case of connections between serial and distributed components. 


## Default behavior

The primary guiding principal for default `src_indices` is to always assume local-process data transfers. 
By "default" we are specifically addressing the situation where a connection is made (either via `connect` or `promote`) without any `src_indices` specified. 
In this case, OpenMDAO is asked to assume what the `src_indices` should be, or in other words to use default `src_indices`. 

There are four cases to consider: 
- serial->serial 
- distributed->distributed
- serial->distributed 
- distributed->serial 

### serial->serial 
Serial variables are duplicated on all processes, and are assumed to have the same value on all processes as well. 
Following the "always assume local" convention, a serial->serial connection will default to `src_indices` that transfer the local output copy to the local input.
However, for serial variables OpenMDAO expects the user to give those src indices relative to the local size of the variable, regardless of which process you happen to be on. 
This keeps the interface uniform and unchanging regardless of the number of processes allocated. 

Example: Serial output of size 5, connected to a serial input of size 5; duplicated on three procs. 
If no `src_indices` are given, then the default on each processor would assumed to be: 
- On process 0, default src_indices=[0,1,2,3,4]
- On process 1, default src_indices=[0,1,2,3,4]
- On process 2, default src_indices=[0,1,2,3,4]

Internally OpenMDAO offsets the indices to enforce local data transfers:
- On process 0, effective src_indices=[0,1,2,3,4]
- On process 1, effective src_indices=[5,6,7,8,9]
- On process 2, effective src_indices=[10,11,12,13,14]


### distributed->distributed
Since these are distributed variables, the size may vary from one process to another. 
Following the "always assume local" convention, the size of the output must match the size of the connected input on every processor and then the `src_indices` will just match up with the local indices of the output. 

Example: distributed output with sizes 1,2,3 on ranks 0,1,2 connected to a distributed input. 
- On process 0, default src_indices=[0]
- On process 1, default src_indices=[1,2]
- On process 2, default src_indices=[3,4,5]

Since the variables are distributed, OpenMDAO does not do additional internal mapping of these src indices

### serial->distributed (deprecated)
Connecting a serial output to a distributed input does not make much sense.
It is recommended that you change the type of the input to be serial instead. 
However, for backwards compatibility reasons default `src_indices` for this type of connection needs to be supported. 
It will be removed in OpenMDAO V4.0

If no `src_indices` are given, then the distributed input must take the same shape on all processors to match the output. 
Effectively then, the distributed input will actually behave as if it is serial, and we end up with the same exact default behavior as a serial->serial connection. 

### distributed->serial (not allowed by default)
This type of connection presents a contradiction, which prevents any unambiguous assumption about `src_indices`. 
Serial variables must take the same size and value across all processes. 
While we could force the distributed variable to have the same size across all processes, the same-value promise still needs to be enforced somehow. 

The only way to ensure that would be to make sure that both the size and `src_indices` matches for the connections across all processes. 
However any assumed way of doing that would violate the "always assume local" convention of the POEM. 

So this connection will raise an error during setup if no `src_indices` are given. 
If `src_indices` are specified manually then the connection is allowed. 


## How to achieve non-standard connections

There are some cases where a user may want to use non default `src_indices` or to connect a mixture of serial or distributed variables.
OpenMDAO supports this by allowing you to explicitly provide whatever `src_indices` you like to `connect` and `promotes`. 
In this case, the default assumptions don't apply. 

This capability remains the same before and after POEM_046. 
All that is changing is the default behavior when no `src_indices` are given. 


## `shape_by_conn` functionality
POEM_046 relates to POEM_022 because of the overlap with the APIs proposed here and their impact on the `shape_by_conn` argument to `add_input` and `add_output`. 

To start, consider the following philosophical view of how `shape_by_conn` and default `src_indices` interact. 
Inputs and outputs are sized as part of their declarations, inside the component definitions. 
They are then connected inside the setup/configure methods of groups. 
Generally, component definitions are in different files --- or at least different parts of the same file --- from group definitions. 
So we can assume that you would not normally see the size of a variable in the same chunk of code that you see how its connected. 
When you see a connection with default `src_indices` you won't necessarily know if either side I/O pair has been set to `shape_by_conn`, 
but you should still be able to clearly infer the expected behavior from the "always assume local" rule. 

The conclusion of this is that `shape_by_conn` should have no direct impact on the default `src_indices`. 
It should give an identical result to the analogous situation where the I/O pair happened to have the same size on each process and were connected with default `src_indices`. 
The result of this is that `shape_by_conn` will be symmetric with regard to whether the argument is set on the input or output side of a connection. The resulting size of the unspecified variable will be the same as the local size on the other side of the connection. 

# Backwards (in)compatibility

## Deprecation of the 'distributed' component option

Prior to this POEM, the old API was to set `<component>.options['distributed'] = <True|False>`. 
As noted in the overview, components themselves are not actually serial or distributed, 
so this doesn't make sense. 
The option will be deprecated, scheduled to be removed completely in OpenMDAO 4.0. 

While deprecated the behavior will be that if this option is set,
then **ALL** the inputs and outputs will default their `distributed` setting to match this option. 
Users can still override the default on any specific variable by using the new API. 

This behavior should provide almost complete backwards compatibility for older models, 
in terms of component definitions, with a few small exceptions. 
See the section on connections for more details. 

## Change to the default behavior of connections with shape_by_conn

The original implementation of `shape_by_conn` stems from POEM_022. 
The work provides the correct foundation for this feature, 
but POEM_022 did not specify expected behavior for serial->distributed or distributed->serial connections, 
and some of the original implementations did not default to "always assume local". 


### Behavior before POEM 46 

#### serial -> distributed 
- the local size of the distributed input is the found by evenly distributing the local size of the serial output  
- example:  [5] -> (2,2,1)

#### distributed -> serial
- the local size of the serial input is the sum of the local sizes of distributed output on each processors   
- example:  (2,2,1) -> [5]

### Behavior after POEM 46 

#### serial -> distributed (deprecated! Will be removed in V4.0)
- the local size of the input on each processor is equal to the local size of the serial output  
- example:  [5] -> (5,5,5)

#### distributed -> serial
- An error will be raised since if no `src_indices` are given

