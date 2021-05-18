POEM ID: 049    
Title: Removal of matrix-matrix derivative APIs  
authors: [justinsgray, naylor-b]   
Competing POEMs: N/A   
Related POEMs: N/A   
Associated implementation PR:   

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

In the early development of OpenMDAO, there the cost of computing total derivatives was heavily impacted by cost of doing matrix-vector products using the DictionaryJacobian directly. 
This performance issue did not affect components that used the matrix-free APIs as strongly (`compute_jacvec_product`, `apply_linear`, `solve_linear`). 
It did, however, strongly impact components that used the full-Jacobian APIs (`compute_partials`, `linearize`). 

At the time, one proposed solution was to include not only a matrix-vector product API, but also a matrix-matrix product API as well. 
This would limit the number of loops over the internal dictionaries and offer better performance. 
In practice this offered only a modest speed up and only in very specific situations when there was no feedback between components. 

Later the AssembledJacobian classes were added which allowed for much more efficient interaction with partial derivative data, and better overall performance. 
The newer features have eliminated the need for the matrix-matrix APIs, which now go unused (at least to the knowledge of the development team). 

Description
-----------

The two APIs primary relevant to this POEM are [`compute_multi_jacvec_product`](http://openmdao.org/twodocs/versions/3.9.1/features/core_features/defining_components/explicitcomp.html?highlight=vectorize_derivs#explicitcomponent-methods) (explicit components) and [`apply_multi_linear`](http://openmdao.org/twodocs/versions/3.9.1/features/core_features/defining_components/implicitcomp.html?highlight=vectorize_derivs#implicitcomponent-methods), `solve_multi_linear` (implicit components). 
In addition to there is also the `vectorize_derivs` argument to the `add_constraint` and `add_design_var` driver methods. 

The three component methods would only get used when `vectorize_derivs` was set to True. 
If you have never implemented any of these methods, or if have never turned on the `vectorize_deriv` option then this API change will not affect you at all. 

All three methods, and the associated `vectorize_derivs` argument to the driver methods will be removed from the code base and docs. 


Backwards Compatibility
------------------------

Removing these APIs will be a completely backwards in-compatible change, 
because the APIs are being removed and not replaced. 
To ease the transition, a patch release will be made that will deprecate the APIs without removing them. 

The APIs will be fully removed in V4.0
