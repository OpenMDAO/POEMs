POEM ID: 048   
Title: Semistructured Training Data for MetaModel   
authors: justinsgray   
Competing POEMs: N/A   
Related POEMs:   
Associated implementation PR: 2185   

#  Status

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

# Motivation

Semi-structued training data occurs frequently in engineering applications like performance maps for turbine engine performance, propeller performance, aerodyanmic drag, etc.
A simple example of semistructured training would a mostly structured grid, but where a few data points are missing on one area of the grid.

Due to the prevalence of this kind of data, it would be valuable to support interpolation of it natively by the existing interpolation component.

# Description

The underlying interpolation routines used in MetaModelStructuredComp component already have the ability to process semistructured data,
but the training data API does not allow for it because it expects fully structured data.
POEM_048 proposes expansion of this capability to support Semi-structured data as well.


# Definition of semi-structured data

Semi-structured data consists of nested sets monotonically increasing arrays of input values paired to arbitrary output values (i.e. outputs need not be monotonic)

This is an example of semistructured data with 2 inputs (x,y)  and one output (z):
```
x = 1
    y = 1, 2, 3, 4
    z = 10, 20, 30, 40
x = 2
    y = 3, 4, 6
    Z = 60, 80, 120
x = 3
    y = 10, 11
    z = 300, 330
```
Semi-structured is different from structured data, because you do not have a complete grid of training data.


A structured data set for the same example as above would be:
```
x = 1
    y = 1, 2, 3, 4, 5, 10, 11
    z = 10, 20, 30, 40, 50, 100, 110
x = 2
    y = 1, 2, 3, 4, 5, 10, 11
    Z = 60, 80, 100, 200, 220
x = 3
    y = 1, 2, 3, 4, 5, 10, 11
    z = 300, 330, 120, 150, 300, 330
```

## Potential data formats for semi-structured data

Formatting semi-structured data is a bit more difficult than structured data.
For structured data you need a 1D array for each input variable, and an ND array of training data with each dimension matching the length of one of the input arrays.
```python
# Structured Data inputs
x = [1,2,3]
y = [1,2,3,4,5,10,11]

# can use meshgrid to create a 3D array of test data
X,Y = np.meshgrid(x, y, indexing='ij')
Z = 10*X*Y
```
This format fits easily into NDarrays, matching with how inputs on OpenMDAO components work.
This is important, because MetaModelStructuredComp offers the ability to have the training data as input to the component, so it could be computed by some upstream part of the model.
The goal is to retain this feature for semi-structured data as well.

A simple semi-structured data format is a list-of-lists:
```python
# Semi-structured data inputs
X = [1,2,3]
Y = [[1,2,3,4],
     [3,4,5],
     [10,11]]
# semi-structured data outputs
Z = [[10,20,30,40],
     [60,80,100],
     [300, 330]]
```

The simplest way to store and utilize this data is to flatten it into a single-dimension list.
```python
# Semi-structured data inputs
X = [1, 1, 1, 1, 2, 2, 2, 3, 3]
Y = [1, 2, 3, 4, 3, 4, 5, 10, 11]
# semi-structured data outputs
Z = [10, 20, 30, 40, 60, 80, 100, 300, 330]
```
In this format, the points are in a strictly ascending order for the (X, Y) pairs.

# Primary considerations for selecting a data format

## Compute cost of interpolation

The interpolation algorithms must do a large amount of bisection-searching of input arrays to find boundary conditions for any interpolation.
The performance of these searches impacts the compute cost of interpolation.
Poor choice of data format could have negative impact on the cost of the searchers.

## Fixed training data use case

If you have a single fixed set of training data (e.g. a fixed efficiency map for a propeller) that you only need to be able to interpolate on,
then you only need to provide that data one time during instantiation.
In this were the only use case, then preference would be given to the most easily worked with data format.
The data could be stored in a properly formatted text file, and a pointer to that file given to the interpolation component.

You would not even need to create inputs on the interpolation component boundary for the training data,
so there would be no concerns about compatibility of the data format and OpenMDAO's input format.

## Changing training data use case

If the training data is expected to change during an analysis/optimization (e.g. you are computing the training data itself as part of the model) then you do need to consider compatibility with OpenMDAO's input format.
An example of would be for aircraft sizing when the geometry is changing so you may compute vehicle aerodynamics at a predetermined set of points to fill out the meta-model which is then used as in a trajectory analysis.
A similar process could be used for generating engine performance data for aircraft sizing, when the engine design itself was part of the design loop.

The proposed flat specification of the training outputs is compatible with OpenMDAO's internal data storage.

## Semi-structured vs. unstructured interpolation

It is not strictly necessary to support semi-structured data as a separate data format,
because OpenMDAO already supports an unstructured format that could be used.
However the unstructured format is less flexible in the kind of interpolations that can be used
and effectively requires you to put more care into the construction of the surrogate itself.

Many users find the pure interpolation based results preferable, even though they often offer lower performance, because of their simplicity of use.
Semi-structured data is capable of being used with the same interpolation routines and hence OpenMDAO should offer this feature.

# API for MetaModelSemiStructuredComp

## Data format
For ease of human readability, ease of data entry, and compabitiliy with the unstructured interpolation algorithms,
the simplest text based data format is selected:
```python
# Semi-structured data inputs
X = [1, 1, 1, 1, 2, 2, 2, 3, 3]
Y = [1, 2, 3, 4, 3, 4, 5, 10, 11]
# semi-structured data outputs
Z = [10, 20, 30, 40, 60, 80, 100, 300, 330]
```

## SemiStructuredMetaModelComp API

The component class, named MetaModelSemiStructuredComp, will have the following APIs:

```python
interp = om.MetaModelSemiStructuredComp(method='scipy_slinear')

# set up inputs and outputs
interp.add_input('x', 0.0, training_data=x, units=None)
interp.add_input('y', 1.0, training_data=y, units=None)


interp.add_output('z1', 1.0, training_data=z1, units=None)
interp.add_output('z2', 1.0, training_data=z2, units=None)
```
