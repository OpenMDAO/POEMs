POEM ID: 067  
Title: Add a method to Vector to compute a hash.  
authors: @naylor-b  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2534](https://github.com/OpenMDAO/OpenMDAO/pull/2534)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

There may be occasions when a developer may want to detect if a Vector has changed without having to
keep a copy of the Vector around in order to be able to detect differences between the Vector's old
and new versions.  Computing a hash of the Vector would provide a simple way to accomplish this.

## Proposed solutions

The following new method will be added to the Vector class.

```
def get_hash(self, alg=hashlib.sha1):
    """
    Return a hash string for the array contained in this Vector.

    Parameters
    ----------
    alg : function
        Algorithm used to generate the hash.  Default is hashlib.sha1.

    Returns
    -------
    str
        The hash string.
    """
```

## Example

To compute a hash for our inputs vector for example:

```
self.oldhash = self._inputs.get_hash()
```

Then later, to detect if the inputs have changed:

```
newhash = self._inputs.get_hash()

if self.oldhash == newhash:  #  self._inputs have not changed
    # reuse cached solution
else:   # self._inputs have changed
    self.oldhash = newhash
    # recompute solution and save it to cache
```

