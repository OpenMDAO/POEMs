POEM ID: 046  
Title: Definition of serial and parallel variables
authors: [@justinsgray]  
Competing POEMs: N/A  
Related POEMs: 022  
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


## Description

Before dealing with the serial/distributed connections, 
it is important to first discuss exactly where the serial/distributed applies in an OpenMDAO context. 

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
Processor allocation is a different topic though, and for the purposes of POEM 046, we will assume that we are working with a simple single comm model setup. 

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



## Example



## Notes on other options that were considered

There were some designs that were considered but rejected. They are being briefly noted here for completeness and because in some cases the pitfalls were not immediately obvious 

### Allowing inputs to be defined as serial/distributed
This seems attractive, because it removes a lot of ambiguity in the expected behavior. 
If an input is `serial` then its size and value are always the same on every proc. 
If it is `distributed` then its size and value are arbitrary on each processor. 

One problem here is that there is no good (re: cheap) runtime way to guarantee the `serial` promise of same-value. 
You can error check the size via a one-time distributed communication at setup, and raise an exception if they don't all match. 
You could also do some error checking on the src_indices, and based on the connected source ensure that things are set up to respect the same-value assumption. 

However, the catch here is the following "... error checking on the src_indices, and based on the connected source ..."
Fundamentally it is the details of the connection into the input that determine its behavior. 
This means that input really doesn't have a serial-ness or distributed-ness itself, 
but is imbued that quality by the information that is passed into it. 

Hence it feel semantically incorrect to give it a label as such, 
despite the fact that it would be convinent from an error checking standpoint. 

It is fundamentally different to say that an output is serial, because that affect the local/global sizes of the variable that OpenMDAO tracks. 
It truly does change the nature of the variable. 


### Allowing per-variable definition of serial/distributed
One of the clarifications of this POEM is to make serial-ness or distributed-ness apply only to the variables and not to the component itself. 
A natural extension of that is to consider letting it be on a variable by variable basis. 

One minor problem with this approach is whether or not "same value" guarantee of serial variables should be enforced by OpenMDAO itself. 
Should OpenMDAO do a broadcast from Rank 0 to the rest of the ranks for you, if you have labeled the variable as serial? 
The that might or might not be actually necessary. 
In all likelihood if you are doing any distributed calculations in your component then you already handled this broadcast on your own if it was needed. 
However, some users might expect OpenMDAO to do this for them for any variable labeled `serial`.  
Hence, we've potentially introduced a whole new ambiguity. 
Conversely if a component's outputs are purely serial or purely distributed then the responsibility of the component developer seems clear. 
They must handle the internal broadcast themselves if they want distributed outputs, where one behaves like a serial case. 

If you have a component doing internally distributed calculations, but has a serial output, then it is required that they broadcast that value out to all procs and set it on all procs. 
There is no good (re: cheap) way for OpenMDAO to make sure that you got this right, 



