POEM ID: 036  
Title: Serialization of Kriging training weights  
authors: dakror  
Competing POEMs:  
Related POEMs:  
Associated implementation PR:  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation

When using (multiple) Kriging surrogate models, the time to train them using the SciPy minimize function can be very time intensive. It might be therefore of interest to train the surrogate in an external or previous iteration of the problem, serialize the trained weights and load this cache in the execution of the actual / full model.


## Description

Inspired by the PR https://github.com/OpenMDAO/OpenMDAO/pull/1541 some way of serializing and loading the trained weights of a Kriging Surrogate model is needed to facilitate this functionality. 

Instead of using Pickle however, which is very sensitive to host and Python environment changes, and also saves data in an insecure, arbitrary, binary, slow and memory-intensive manner, we suggest using JSON as its more flexible than just using plain CSV table files and also  comes with native support by the Python runtime. There are more optimal formats available, like PyTables or even HDF5, but these require external libraries. JSON files can be easily exchanged, compressed and even manually inspected.

The encoding of the JSON file would follow the aforementioned PR, by creating one root object with the following structure:

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

In order to save the training weights after the model actually has been initially trained, a new option in the Kriging surrogate model is needed to specify a filename for output of the training weights. While specifying a simple file path could prove to be easy to use and understand, however accepting a file-esque object (as well?) could provide the benefit of also being able to capture the data in-program, for instance using `StringIO` or directly into deflate using `ZipFile`. Being this flexible would come only at the cost of the option type-hint being unavailable.

A suggestion would be:

```py
self.options.declare('training_cache_output', default=None,
                     desc='Cache the trained model to avoid repeating training')
```


### Loading trained data

Similarly, in order to load the training weights, an option for an input filename / file-esque object is needed:

```py
self.options.declare('training_cache_input', default=None,
                     desc='Fetch the cached training weights to avoid repeating training')
```

Another benefit over Pickle is the possibility of verifying the data dimensions at the point of loading directly, or raising an exception to the caller.

As with the PR, the actual loading of the given input file would occur in the `train()` method. This change is opaque to the other methods of the Surrogate.

### Further extension

When using multiple Kriging surrogates, it might be even better to save all models to a single file using a unique identifier each, instead of creating multiple files, one per surrogate. The class would need to statically keep track of used IDs in order to detect and deny duplicates. The options would need to be augmented with an ID specification.