POEM ID: 106  
Title: Expose JAX vectorization to users  
Author: mtfang (Michael T. Fang)   
Competing POEMs: N/A  
Related POEMs: [POEM_84](https://github.com/OpenMDAO/POEMs/blob/master/POEM_084.md)  
Associated implementation PR: N/A  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

Motivation
==========
OpenMDAO exposes two of the three key features of JAX to users: autograd and JIT. Autograd provides convinence for the user so
they no longer have to write analytic derivatives and JIT provides performance benefits. Vectorization via `vmap` is
the third key feature of JAX which can provide benefits for further performance improvement in the context of analysis.

Description
===========

Problem vectorization is a natural way to run performant analysis sweeps. Vectorized OpenMDAO problems also opens the door
to using machine learning libraries for optimization (Optax) or probablistic modeling (Blackjax). Exposing vectorization
could happen into two ways:

1. make output values traceable w.r.t. input values and have the user functionalize the problem
2. provide a standard interface such that a problem given a set of inputs and outputs can be transformed into a function

Users also will invest time to refactor their model with JAX. This provides better externalization of
these models in other frameworks so that time invested in JAX-ifying code pay dividends elsewhere.

Example
-------

Here we would like to run a vectorized sweep over a set of two input parameters `x` and `y` and obtain the output `z`.
Wrapping the set of statements to 1. set component values, 2. run the model, and 3. get component values in a function
enables input vectorization.

```
import jax
import jax.numpy as jnp
imoprt openmdao.api as om

prob = om.Problem()
prob.model.add_subsystem("comp", ExampleComponent())
prob.setup()

def z(prob, x, y):
    # right now, various methods under the hood casts inputs as a numpy array so they cannot be traced
    prob.set_val("comp.x", x)
    prob.set_val("comp.y", y)
    prob.run_model()
    return prob.get_val("comp.z")

# grad function for partials of z w r.t. x and y
grad_z = jax.grad(z, argnums=(1, 2))

# vmap over x and y
jax.vmap(z, in_axes=(None, 0, 0))(
    prob,
    jnp.linspace(1, 20, 100),
    jnp.linspace(0.1, 0.5, 100)
)

# vmap over the partials of z w.r.t. x and y
jax.vmap(grad_z, in_axes=(None, 0, 0))(
    prob,
    jnp.linspace(1, 20, 100),
    jnp.linspace(0.1, 0.5, 100)
)
```

References
----------
1. https://docs.jax.dev/en/latest/automatic-vectorization.html
2. https://optax.readthedocs.io/en/latest/
3. https://blackjax-devs.github.io/blackjax/
