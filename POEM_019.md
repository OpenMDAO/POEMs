POEM ID: 019   
Title:  Random Vectors in Directional Derivatives   
authors: [kejacobson] (Kevin Jacobson)   
Competing POEMs: [N/A]   
Related POEMs: [N/A]   
Associated implementation PR:   

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

This POEM is a request for an additional option for partial derivative checking with directional derivatives.
The motivating use case is partial checking of high-fidelity analysis components that may have large input and output vectors.
For those types of components, directional derivatives are essential
The current vector in the implementation of directional derivatives is a uniform vector of ones, [1,1,1,1,...], but this is inadequate for testing some types of components.
For example, a computational fluid dynamics component where the input is the vector of mesh coordinates.
If you apply a uniform perturbation to the mesh coordinates, the mesh translates, but the flow state, lift, drag, etc. will not change.
But, a random perturbation vector can properly exercise the component.
Another example is a component that fits a rotation to a set of displaced points.
With the uniform vector, the rotation is zero and the directional derivative is zero.

Description
-----------

Although it may be possible change the expected type of `directional` from boolean to string, it may be better for backwards compatibility to add a new optional argument to `set_check_partial_options` to control the type of vector.

```
def setup(self):
    self.set_check_partial_options(wrt='*',directional=True,direction='random')
```

The options for `direction` could be `'uniform'`, `'random'`, or `'seeded_random'`.
`'uniform'` is the current approach.
The `'seeded_random'`, potentially seeding on the vector size or some other consistent value, can useful for getting a consistent answer for debugging partials without a uniform vector.
The '`random`' option gives a different perturbation vector each time which is also useful. Running check partials multiple times with a new random vectors gives more confidence in the result.

The pseudocode looks something like:
```

if 'random' in direction:
  if 'seeded' in direction:
    np.random.seed(seed_value)
  self.perturb_vec =  np.random.random_sample(input.shape) - 0.5 # offset to get both positive and negative perturbations
else:
  self.perturb_vec = np.ones(input.shape)

# setting up the finite difference inputs, where delta is the real or complex step size
input_perturbed[:] = input[:] + delta * self.perturb_vec
.
.
.
# setting up the forward mode partial
d_input = self.perturb_vec
```

This method feeds into the [dot product test for adjoints](http://www.reproducibility.org/RSF/book/gee/ajt/paper_html/node20.html) where `perturb_vec` is `m`.
With a second perturbation vector of the size of the outputs, `d`, the forward and reverse mode partials can be checked with one call for the forward mode and one for the reverse mode.
