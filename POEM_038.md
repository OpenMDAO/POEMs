POEM ID: 038  
Title: Raise an error if a user declares a sub-jacobian to have a value of zero.  
authors: [Kenneth-T-Moore]  
Competing POEMs:  
Related POEMs:  
Associated implementation PR:  

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

In an OpenMDAO component, the `declare_partials` method is used to declare which input/output pairs have
derivatives defined. Any pair that is not declared is assumed to be zero. However, at present, you can
also declare a derivative to have a constant zero value like this:

  self.declare_partials(of='y', wrt='x', val=0.0)

To the user, this is currently the same as not declaring the derivative. It is also the same mathematically,
however, there are some important differences:

1. The value 0.0 is stored as a sub-jacobian, so there is some memory overhead associated with storing it. If
any matrix-vector products are computed, there will also be some unnecessary calculation multiplying by zero.

2. In order to calculate the coloring for the total derivatives, a jacobian is generated and filled with
random values. Every entry that is declared is filled, even ones that are declared as 0.0 constants. This
can result in a total derivatives coloring that isn't as efficient as it should be (i.e., requires more
colors than it would if the zero-valued derivative was not explicitly declared.)



## Description

The following:

  self.declare_partials(of='y', wrt='x', val=0.0)

will raise an error in future versions of OpenMDAO.

