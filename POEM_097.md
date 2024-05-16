POEM ID: 097
Title: Quantities to associate values with units.
authors: robfalck (Rob Falck)
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

Some teams have been struggling with ways of providing units as part of options.
For instance, you might have a model parameter associated with physical units but don't care to differentiate with respect to it, and thus pass it as an option.

### Why adding a `units` argument to OptionsDictionary declare_options won't work.

Some users have experiemented with passing tuples as options, where the second value contains units.
This isn't ideal since another unit may expect a tuple that doesn't involve units, leading to ambiguity.

We could implement a set_val/get_val with units, as we do with OpenMDAO vectors.  The existing `OptionsDictionary.set(**kwargs)` and `OptionsDictionary.temporary(**kwargs)` are not compatible with this, nor is the abiltiy to pass options as keyword arguments to to OpenMDAO Systems.

Other Python packages exist that handle units, such as [pint](https://pypi.org/project/Pint/). The notion of a _Quantity_ in pint would work well in OpenMDAO, but the syntax of pint, where units are applied by multiplying them in numerical expressions is not very OpenMDAO-esque.  Furthermore, we'd need to make sure that we utilize unit conversions as OpenMDAO has defined them.  If a user doesn't initialize the pint units registry correctly, they could potentially get inconsistent unit conversions.

However, the notion of an object, a Quantity, that binds a numerical value to a unit is a good idea and would work in OpenMDAO.

## Proposed Solution

OpenMDAO will add a `Quantity` object to the API.

Quantity will, at a minimum, have a `val` and `units` attributes.

### Uses of `om.Quantity`

Quantities will be allowed to be the values for options.

`Problem.__setitem__` will allow values to be set using a Quantity.

`Problem.__getitem__` will **NOT** return a quantity, to maintain backwards compatibility.

For consistency, we will allow them in the `set_val` method, though using them along with the `units` argument will raise an exception.

In the future we could examine returning them from `__getitem__` and `get_val` but that would likely break too much existing code.\

### Differences with the `set_val` API.

We had previously implemented `set_val` and `get_val` to, among other things, allow the specification of units when setting or getting values.

In hindsight, we could have stuck with dict-like access only and implemented some sort of quantity-like object instead, but those methods are useful for other reasons. Admittedly there is some inconsistency here, but for options especially, having a single object encapsulate both values and units seems preferable.

## Example

Declaring Options:

```language=python
   self.options.declare('span', types=(om.Quantity,), default=om.Quantity(45.0, 'ft'))
```

Setting Options

```python
wing.options['span'] = om.Quantity(45.0, 'ft')
```

Setting Values

```python
prob['initial_mass'] = om.Quantity(312.5, 'kg')
```

```python
prob.set_val('initial_mass', om.Quantity(312.5, 'kg'))
```

The following should raise an exception, due to the duplicate specification of units.

```python
prob.set_val('initial_mass', val=om.Quantity(312.5, 'kg'), units='kg')
```

Retrieving values without units

```python
span = self.options['span'].val

print(f'span is {span.val} {span.units})
```