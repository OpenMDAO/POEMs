POEM ID: 107  
Title:  Allow Input-Input Connections (Syntactic Sugar)  
authors: robfalck (Rob Falck)   
Competing POEMs: None  
Related POEMs:  None  
Associated implementation PR:  [#3610](https://github.com/OpenMDAO/OpenMDAO/pull/3610)  

Status:  

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation

In the original incaration of OpenMDAO, unconnected inputs were just left in place. There were a few shortcomings to that approach, such as requiring users to explicitly create `IndepVarComp`s for those inputs, and the inability to compute total derivatives wrt thoses inputs.

The incorporation of the "automatic `IndepVarComp`" alleviated a lot of these issues.
A significant result of this development is that _all_ inputs now have a corresponding output somewhere in the OpenMDAO model.

One of the rules in OpenMDAO had been that input-to-input connections were forbidden.
There was no such thing as a transfer of data from the input vector back to the input vector.

The lack of Input-Input connections causes users to sometimes implement things like "pass-through" components that do nothing but echo an input value into an output value that can be connected somewhere else in the hierarchy.
The alternative to this, promotion, means that a model developer change the namespacing in their model in order to enable these connections-via-promotion.
I would argue that the use of pass-through components in OpenMDAO is an [anti-pattern](https://en.wikipedia.org/wiki/Anti-pattern), and the extra memory and transferred to handle them is not necessary.

## Description

With the advent of the `AutoIVC` capability in OpenMDAO, the fact that each input has a corresponding output somewhere in the model, OpenMDAO can allow input-input connections as [syntatic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar).

During the setup process, OpenMDAO resolves both promotions and manual connections to determine the data flow through a model.

The proposal here is that the syntax

```python
model.connect('c1.x', 'c2.x')
```

be allowed in cases where both `c1.x` and `c2.x` are inputs.
During the setup process, OpenMDAO will determine the output that is connected to `c1.x` and also connect that output to `c2.x`. It can be thought of as telling OpenMDAO "connect `c2.x` to whatever is connected to `c1.x`.

There are at least a few exceptional cases here.

### Case 1: No output is connected to c1.x

When no output is otherwise connected to `c1.x`, OpenMDAO generates an AutoIVC output for it. In this case, that same promoted name, `c1.x` would be used for setting the value of `c2.x`.  That is, when the ultimate source is an AutoIVC this connect statement functionally aliases `c2.x` to `c1.x`.

### Case 2: Circular logic

In allowing input-to-input connections, something like the following becomes possible:

```python
model.connect('c1.x', 'c2.x')
model.connect('c2.x', 'c3.x')
model.connect('c3.x', 'c1.x')
```

OpenMDAO will detect the cyclic behavior and raise an exception.

### Case 3: Multiple layers of src_indices

Imagine a series of connections from one output through a number of inputs.

```
c1.y -> c2.x -> c3.x -> c4.x -> c5.x
```

As OpenMDAO resolves the chain of connections from the ultimate output to the last input, using `src_indices` when connecting `c4.x` to `c5.x` would mean that `c5.x` should be the subset of `c4.x` with those `src_indices` applied.

In the reference PR src_indices in input-to-input connections are not yet implemented and will result an an error.

