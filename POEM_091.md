POEM ID: 091  
Title: Eliminate combined jacobian-based and matrix free capability in a single component.  
authors: naylor-b (Bret Naylor)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [PR 3020](https://github.com/OpenMDAO/OpenMDAO/pull/3020) 

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

Our current implementation allows a component to perform matrix free operations (`compute_jacvec_product` or `apply_linear`) and in addition compute sub-jacobians using `compute_partials` or `linearize`.  This makes it difficult to declare partials for that component in a way that results in the best performance.  OpenMDAO has a new relevance graph
that considers dependencies between individual inputs and outputs of the same component based on which partials are declared within that component, i.e., if no partial is declared for output y with respect to input x, then in the graph, y does not depend on x.

In order to take advantage of this new relevance graph, all components must accurately declare which of their partials are
nonzero.  In the case of a matrix free component, the current implementation will allocate space to contain the corresponding
sub-jacobian for every declared partial.  Some variables in a matrix free component are likely quite large, resulting in
allocation of a very large sub-jacobian.  OpenMDAO currently warns the user when this happens, which discourages the author of
a matrix free component from declaring any partials.  But if the matrix free component doesn't declare any partials, how can
the new relevance graph accurately reflect any internal sparsity within that component?


## Proposed solution

We propose that OpenMDAO will no longer allow a single component to compute both matrix free and jacobian based derivatives.
Each component will be either matrix free or jacobian based, but not both.  Note that matrix free components and jacobian
based components may still be freely mixed within the same model.

This means that a matrix free component can declare partials to inform the framework about its internal sparsity without
allocating any memory for sub-jacobians.

In order to maintain backward compatability, a matrix free component that declares no partials will be treated as if it
declared dense partials, i.e., all outputs depend on all inputs.  However, if a matrix free component declares *any* partials,
then any that are not declared are assumed to be zero.


## Example

In the example below, the matrix free component has an output 'y1' that depends only on input 'x1' and an output
'y2' that depends only on input 'x2'.  Declaring the partials only for 'y1' wrt 'x1' and 'y2' wrt 'x2' tells the
framework that the 'y1' wrt 'x2' and 'y2' wrt 'x1' partials are zero and those connections can be left out of the
relevance graph.


```
class MatFreeComp(om.ExplicitComponent):

    def setup(self):
        self.add_input("x1", val=1.0)
        self.add_input("x2", val=1.0)
        self.add_output("y1", val=1.0)
        self.add_output("y2", val=1.0)

        self.declare_partials('y1', 'x1')
        self.declare_partials('y2', 'x2')

    def compute(self, inputs, outputs):
        outputs['y1'] = 2.0 * inputs['x1']
        outputs['y2'] = 3.0 * inputs['x2']

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'y1' in d_outputs:
                if 'x1' in d_inputs:
                    d_outputs['y1'] += 2.0 * d_inputs['x1']
            if 'y2' in d_outputs:
                if 'x2' in d_inputs:
                    d_outputs['y2'] += 3.0 * d_inputs['x2']
        else:  # rev
            if 'y1' in d_outputs:
                if 'x1' in d_inputs:
                    d_inputs['x1'] += 2.0 * d_outputs['y1']
            if 'y2' in d_outputs:
                if 'x2' in d_inputs:
                    d_inputs['x2'] += 3.0 * d_outputs['y2']
```
