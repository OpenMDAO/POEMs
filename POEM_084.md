POEM ID: 084  
Title: Add a set of jax functions and documentation on using jax with OpenMDAO.  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  [POEM 080: TanhActivationComp](https://github.com/OpenMDAO/POEMs/blob/master/POEM_080.md)  
Associated implementation PR: [PR 2913](https://github.com/OpenMDAO/OpenMDAO/pull/2913)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [x] Integrated

## Motivation

_How many times has the average OpenMDAO developer implemented and reimplemented derivatives for `arctan2` or `norm`?_
The intent of this POEM is to eliminate the need to do so.

Experience with OpenMDAO has shown that chaining many small components together hinders performance by increasing the amount of data being transferred internally, and by reducing the size of the matrices involved for the linear and nonlinear solvers.
Our recent experience with [jax](https://github.com/google/jax) has shown that its automatic differentiation capability can be as performant as analytic derivatives.
While we provide a jax-based function wrapping component to do this, giving users some jax-based function building blocks may be preferred in some cases. This would allow users to tailor the way in which jax computes derivatives for their implementation.  

Through the implementation of some new functions, and documentation of how to incorporate jax's automatic differentiation and just-in-time compilation capabilities into OpenMDAO, we can save users from needing to develop their own analytic partials or suffer through performance issues of complex-step and finite-differencing.

## Proposed Solution

OpenMDAO will contain a new subpackage, `openmdao.jax` that will include jax-based implementations for some useful differentiable functions.

The initial set will include:
- act_tanh : A hyperbolic tangent-based activation function.
- smooth_abs : A smoothed approximation to the absolute value function.
- smooth_max : A smoothed approximation to the maximum value along two different inputs.
- smooth_min : A smoothed approximation to the minimum value along two different inputs.
- ks_max : An implementation of the Kreisselmeier-Steinhauser function for differentiable approximation of the maximum value in an array.
- ks_min : An implementation of the Kreisselmeier-Steinhauser function for differentiable approximation of the minimum value in an array.

`jax` will not become a general dependency of OpenMDAO unless users wish to utilize functions in `openmdao.jax` or their own custom `jax` functions.

### Documentation of usage in a component

`jax` provides a lot of flexibility in how derivatives are calculated, how vectorization is performed, how parallelization is performed, etc.
Instead of providing a jax-specific component that would make some assumption on how the derivatives are computed for a particular model, this capability will feature documentation on how to do so for a few sample models and teach users on when to use a particular approach for differentiation.

The `jit` method in `jax` is also difficult to apply in a one-size-fits-all manner. We will document how to improve the performance of jax-based models using its just-in-time compilation capability.
