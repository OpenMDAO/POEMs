POEM ID: 036  
Title: Serialization of Kriging training weights  
authors: dakror  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/1753  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Motivation

When using (multiple) Kriging surrogate models, the time to train them using the SciPy minimize function can be very time intensive. It might be therefore of interest to train the surrogate in an external or previous iteration of the problem, serialize the trained weights and load this cache in the execution of the actual / full model.


## Description

Inspired by the PR https://github.com/OpenMDAO/OpenMDAO/pull/1541 some way of serializing and loading the trained weights of a Kriging Surrogate model is needed to facilitate this functionality. 

Instead of using Pickle however, which is very sensitive to host and Python environment changes, and also saves data in an insecure, arbitrary, binary, slow and memory-intensive manner, we suggest using the Numpy Binary Format as its more flexible than just using plain CSV table files and offers compression.

NumPy offers a form of dictionary file format, essentially just a zip-file wrapper around their file format NPY. Using `numpy.savez` or `numpy.savez_compressed` a dictionary-like structure can be stored. The following tuples need to be saved:

```json
{
    "X": <...>,
    "Y": <...>,
    "n_samples": <...>,
    "n_dims": <...>,
    "X_mean": <...>,
    "X_std": <...>,
    "Y_mean": <...>,
    "Y_std": <...>,
    "thetas": <...>,
    "alpha": <...>,
    "U": <...>,
    "S_inv": <...>,
    "Vh": <...>,
    "sigma2": <...>,
}
```

### Saving training data

In order to save the training weights after the model actually has been initially trained, a new option in the Kriging surrogate model is needed to specify a filename for output of the training weights.

A suggestion would be:

```py
self.options.declare('training_cache_output', types=str, default=None,
                     desc="Cache the trained model to avoid repeating training and write it to the given file.")
```


### Loading trained data

Similarly, in order to load the training weights, an option for an input filename / file-esque object is needed:

```py
self.options.declare('training_cache_input', types=str, default=None,
                     desc="Fetch the cached training weights to avoid repeating training from given file.")
```

As with the PR, the actual loading of the given input file would occur in the `train()` method. This change is opaque to the other methods of the Surrogate.
