POEM ID: 046  
Title: Definition of serial and parallel variables
authors: [@justinsgray]  
Competing POEMs: N/A  
Related POEMs: 022, 044 
Associated implementation PR:

##  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

As of OpenMDAO 3.8.0 there is significant confusion surrounding connections between serial and distributed variables, what happens when you do or do not specify `src_indices`, and what happens if you use `shape_by_conn` in these mixed serial/distributed situations. 

The main purpose of this POEM is to provide clarity to this situation by means of a clear, concise, and self-consistent explanation. 
Some modest changes to APIs are proposed because they help unify what are currently corner cases under one simpler overall philosophy. 


## Overview of Serial and Distributed Computation in OpenMDAO

Serial vs distributed labels can potentially come into play in three contexts: 
1) Components 
2) Variables
3) Connections

### Components are not classified as serial/distributed
OpenMDAO makes no assumptions about what kind of calculations are done inside the `compute` method of your components. 
**There is no serial/distributed classification of components**. 
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
OpenMDAO can split comms within a model so that it is absolutely possible that a component is only setup on a sub-set of the total processors given to a model. 
Processor allocation is a different topic though, and for the purposes of POEM 046, we will assume that we are working with a simple single comm model. 

### What it means for a variable to be serial or distributed in OpenMDAO

A `serial` variable has the same size and the same value across all the processors it is allocated on. 
A `distributed` variable has a potentially varying size on each processor --- including possibly 0 on some processors --- and a no assertions about the various values are made. 
The sizes are "potentially varying" because its possible to have a distributed variable with the same size on every processor, but this would just be incidental. 

Note that even for a serial variable, there are still multiple copies of it on different processors. 
It is just that we know they are always the same size and value on all processors. 
The size guarantee is easily enforced during model setup. 
The value guarantee is a little more tricky because there are two ways to achieve it: 
- Perform all calculations on a single processor and then broadcast the result out to all others 
- Duplicate the calculations on all processors and use the locally computed values (which are the same by definition because they did the same computations)

OpenMDAO supports both ways, but defaults to the duplicate calculation approach. 
If you need/want the broadcast approach, you can manually set that up. 

### Places where serial/distributed labels impact OpenMDAO functionality

In general, internally OpenMDAO does not make an actual distinction between serial and distributed variables. 
It does not affect the data allocation, nor the data transfers at run time. 
There are a few places where it can have an impact though: 
- For serial variables OpenMDAO can check for constant size across processors
- When allocating memory for partial derivatives, it is critical to know the true size of the variables. 
- When computing total derivatives the framework needs to know if values are serial or parallel to determine the correct sizes for total derivatives, and also whether to gather/reduce values from different processors.

To understand the relationship between serial/distributed labels and partial and total Jacobian size consider this example (coded using the new proposed API from this POEM): 

```python
import numpy as np

import openmdao.api as om 

class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo')

        DISTRIB = True
        if DISTRIB: 
            self.out_size = self.comm.rank+1
        else: 
            self.out_size = 3
            self.add_output('bar', shape=self.comm.rank+1, distributed=DISTRIB)

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
with `self.options['distributed'] = True` you would see the total derivative of `foo` with respect to `bar` is a size (6,1) array: `[[2],[2],[2],[2],[2],[2]]`.
The length of the output here is set by the sum of the sizes across the 3 processors: 1+2+3=6. 
Each local partial derivative Jacobian will be of size (1,1), (2,1), and (3,1) respectively. 

With `self.options['distributed'] = False` you would see the total derivative of `foo` with respect to `bar` with respect to `bar` is a size (3,1) array: `[[2],[2],[2]]`.
The local partial derivative Jacobian will be of size (3,1) on every processor. 


## API for labeling serial/distributed variables

a `distributed` argument will be added to the `add_input` and `add_output` methods on components. 
The default will be `False`. 
Users are required to set `distributed=True` for any variable they want to be treated as distributed. 

one serial input (size 1 on all procs), 
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
one serial output (size 10 on all proc).
```python
class TestComp(om.ExplicitComponent): 

    def setup(self): 

        self.add_input('foo', distributed=True)
        self.add_output('bar', shape=(10,))
```

This API will allow components to have mixtures of serial and distributed variables. 
For any serial variables, 
OpenMDAO will be able to check for size-consistency across processors during setup.
In according with POEM_044, it should be possible to control whether this check happens or not.   

Although value-consistency is in theory a requirement for serial variables in practice it will be far to expensive to enforce this. 
Hence it will be assumed, but not enforced. 

## Connections between serial and distributed variables

In general there are multiple ways to handle data connections when working with multiple processors. 

Serial or distributed labels are a property of the variables, 
which are themselves attached to components. 
However, the transfer of data from one component to another is governed by `connect` and `promotes` methods at the group level. 
When working with multiple processors, you have to consider not just which two variables are connected but also what processor the data is coming from too. 
This is all controlled via the `src_indices` that are given to `connect` or `promote` methods on `Group`. 

One of primary contributions of POEM_046 is to provide a simple and self consistent default assumption for `src_indices` in the case of connections between serial and distributed components. 


### Default behavior

This POEM proposes that the primary guiding principal for `src_indices` defaults should be to always assume local-process data transfers if possible. 
By "default" here, we are specifically addressing the situation where a connection is made (either via `connect` or `promote`) without any `src_indices` specified. 
In this case, OpenMDAO is asked to assume what the `src_indices` should be. 

There are four cases to consider: 
- serial->serial 
- serial->distributed 
- distributed->serial 
- distributed->distributed

#### serial->serial 
Recall that serial variables are duplicated on all processes, and are assumed to have the same value on all processes as well. 
So following the "always assume local" convention, a serial->serial connection will default to `src_indices` that transfer the local output copy to the local input.

Example: Serial output of size 5, connected to a serial input of size 5; duplicated on three procs. 
On process 0, the connection would have src_indices=[0,1,2,3,4]. 
On process 1, the connection would have src_indices=[5,6,7,8,9]. 
On process 2, the connection would have src_indices=[10,11,12,13,14]. 

Note: If you would like to force a data transfer to all downstream calculations from the root proc instead, you can manually specify the src_indices to be [0,1,2,3,4] on all processors. 

#### serial->distributed 
Here you have a serial output, which is duplicated on all processors, connected to a distributed input. 
In this case, if no src_indices are given, then the distributed input must take the same shape on all processors to match the output. 
Effectively then, the distributed input will actually behave as if it is serial, and we end up with the same exact default behavior as a serial->serial connection. 



### How to achieve non-standard connections

### `shape_by_conn` functionality
This POEM (044) related to POEM_022 because of the overlap with the APIs proposed here and their impact on the `shape_by_conn` argument to `add_input` and `add_output`. 

- `shape_by_conn` for non local data transfers should not be allowed??





## Backwards compatibility

Prior to this POEM, the old API was to set `<component>.options['distributed'] = <True|False>`. 
This will be deprecated, scheduled to be removed completely in OpenMDAO 4.0. 

While deprecated the behavior will be that if this option is set,
then **ALL** the inputs and outputs will default their `distributed` setting to match this option. 
Users can still override the default on any specific variable by using the new API. 

This behavior should provide complete backwards compatibility for older models, 
in terms of component definitions. 
However there is one caveat, related to proposed changes in to how connections and associated `src_indices` are handled. 
See the section on connections for more details. 








