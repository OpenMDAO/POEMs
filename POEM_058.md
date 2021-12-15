POEM ID: 058  
Title: Fixed grid interpolation methods  
authors: Kenneth-T-Moore  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [OpenMDAO/OpenMDAO#2285 : Initial implementation of 3D-slinear and 1D-akima](https://github.com/OpenMDAO/OpenMDAO/pull/2285)  
                              [OpenMDAO/OpenMDAO#2300 : Full vectorization and caching for fixed interpolation methods.](https://github.com/OpenMDAO/OpenMDAO/pull/2300)  
                              [OpenMDAO/OpenMDAO#2314 : Initial implementation of 3D-lagrange3.](https://github.com/OpenMDAO/OpenMDAO/pull/2314)  
                              [OpenMDAO/OpenMDAO#2325 : More speed improvements for 3D-lagrange3.](https://github.com/OpenMDAO/OpenMDAO/pull/2325)  
                              [OpenMDAO/OpenMDAO#2329 : Consistent naming scheme, as per this POEM.](https://github.com/OpenMDAO/OpenMDAO/pull/2329)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

It is a common feature in many engineering analyses to have variables whose value is defined by a table that contains a regular
grid of points spanning the input dimensions. The table data may come from experiments or measurements or may be the result of an
intensive computation, and thus is only available at the limited set of points. For gradient optimization of the model, we need to
be able to compute values and derivatives for any table output when the requested inputs don't fall on table values -- this is called
interpolation.

OpenMDAO provides two ways to interpolate on a table.  The simplest way is to use `MetaModelSemiStructuredComp`. Here is an example where
it is used for a simple 2-dimensional table with 4 points.

```python
import openmdao.api as om

x_points = np.array([0.2, 0.6]
y_points = np.array([0.0, 1.0]
f = np.array([[16.0, 23.0], [14.5, 2.3]])

# Create regular grid interpolator instance
interp = om.MetaModelStructuredComp(method='slinear')

# Inputs
interp.add_input('x', 0.0, training_data=x_points))
interp.add_input('y', 1.0, training_data=y_points))

# Output
interp.add_output('xor', 1.0, training_data=f)
```

Likewise, OpenMDAO also provides a stand-alone interpolation object that you can incorporate into a custom component, though the
strongest case for using it is for one-time computation during model setup.

```python
interp = InterpND(method='lagrange3', points=(x_points, y_points), values=f)

# Compute new value and derivative
new_point = np.array([0.45, 0.66])
f, df_dx = interp.interpolate(new_point, compute_derivative=True)
```

The "method" argument informs OpenMDAO which method to use from a list of implemented methods. Choosing this method is an important
decision that impacts both accuracy and performance. In general, higher-order methods use more of the surrounding points to produce
a better fit, but have slower computational times. Certain methods also assure continuity of first or second derivatives.

Some benchmarking of recent optimizations on our system models has identified interpolation speed as the overwhelming contributor
to runtime (more so for objective computation time rather than gradient time). The tables in these models are typically 3-dimensional,
using higher-order methods such as "lagrange3" and "cubic", though there are some that use "slinear" as well.  Moreover, the problem
is exacerbated by the model's use of implicit time simulation via dymos, which requires interpolation to be run at each time point.
The need for interpolation approaches that reduce the runtime by at least an order of magnitude is the motivation for this POEM.

After some initial investigation, we are confident that we should be able to greatly improve interpolation speed if we create
a set of new methods that presume fixed table sizes and allow fully vectorized computation for use in dymos. The new approach
will be explained below.

## Fixed-Grid Interpolation Methods

The existing table-based interpolation strategy in OpenMDAO is very flexible -- the table can be any size, and the table
values can all change at runtime. Some more details about the flexible implementation are described below.

*Flexible Dimension*: The existing interpolation methods allow a table to be defined for any number of
dimensions. In multi-dimensional interpolation, each dimension is treated successively. For example, if you are interpolating on
a 1-dimensional table with "lagrange3", then you use 4 points, two of which are on the left side of the point your interpolating,
and two on the right. For a 2-dimensional table, we again need 4 points in the first dimension, but then each of those points
must be interpolated on the second dimension, requiring 4 points each. That gives a total of 16 points to evaluate. Note that
this operation is done "all-at-once" in a numpy array, rather than looping over the second dimension.

*Table Values can Change*: While the table points are fixed, the values are allowed to change if the "training_data_gradients"
option on `MetaModelStructuredComp` is set to True. The derivatives of the interpolated output with respect to the values are
also computed in this case.

In general, interpolation can be split into three phases:

1. Bracket (Find the cell that the requested point lies in)
2. Compute Coefficients (These are functions of the table values and grid locations)
3. Compute Value and Derivative (Represented by a polynomial of the table variables using the coefficients from 2.)

There are several things that can be done to make each of these phases more efficient.

A python algorithm is currently used for bracketing, and it isn't vectorized, so it must be looped to bracket multiple points.
The numpy `searchsorted` provides a vectorized alternative. Local testing found it to be slower for bracketing a single
point, but it achieved parity at a `vec_size` of 2, and is much faster for larger sizes. We will keep the old python bracketing
algorithm to use for single-width vectors and use `searchsorted` for larger sizes.

Additional performance can be gained by saving the coefficients computed in step 2 into a cache so that they can be reused the
next time a point is requested in that cell. This is only possible if the table values are fixed. It also requires determining
the equation for interpolation across all dimensions and expanding it into powers of the input variables. The number of
coefficients is a function of the number of dimensions in the table and the order of the interpolation method. Since this
requires writing the equations across the entire interpolation, it isn't feasible to keep the flexibility with dimension. We
need a separate implementation for each table size.

Finally, it is important to make sure that step 3 is as efficient as possible. It is not expected that a typical optimization
would request points from all over the table, but instead would most likely hone in on a few cells. Thus, the coefficients will
be cached quickly, so interpolation from that point only requires step 1 and step 3, with some `set` operations in between to
check for new uncached points. We can improve performance by vectorizing this step (as well as step 2, though for that, we need to
compute the set of uncached coefficients simultaneously.) The numpy function `einsum` will help with high-dimensional matrix
operations.

## Naming Convention for the New Algorithms

The new methods will be available on `MetaModelSemiStructuredComp` and `InterpND`, and their names will include "#D-" prepended to the
algorithm name. So, a fixed implementation of "akima" on a 1-dimensional grid will be called "1D-akima".

```python
comp = om.MetaModelSemiStructuredComp(method='3D-lagrange3', extrapolate=True)
```

## Implementation Considerations

### slinear

For linear interpolation on a 3D grid, a solution exists; it is usually called "trilinear" in the literature. It is straightforward
to implement, with 8 coefficients to compute.

The following shows performance interpolating 100000 times over a 25x15x12 table.

| vec_size | slinear | 3D-slinear   |
| :---     |  ---:   |         ---: |
| 1        | 0.4364  | 0.2624       |
| 2        | 0.7614  | 0.7012       |
| 10       | 3.487   | 0.5921       |
| 50       | 17.42   | 0.6773       |


### lagrange2 and lagrange3

The lagrange methods pose some challenges. The most important for our models is lagrange3 on a 3-dimensional table. This requires the
computation of 64 coefficients, each of which is the sum of 64 terms that arise from taking the outer product of three third-order polynomials,
one for each dimension.  Fortunately, this can be done efficiently in a single `einsum` call.

The following shows performance interpolating 10000 times over a 25x15x12 table.

| vec_size | lagrange3 | 3D-lagrange3  |
| :---     |  ---:     |          ---: |
| 1        | 0.9359    | 0.4376        |
| 2        | 1.722     | 0.6817        |
| 10       | 8.434     | 0.8769        |
| 50       | 41.08     | 1.707         |


### akima

The akima method is fairly straightforward to rework in 1D. However for higher dimensions, it is not yet clear that it can be expanded
and factored into a form that works.

The following shows performance interpolating 10000 times over a 25 element table.

| vec_size | akima   | 1D-akima  |
| :---     |  ---:   |       --: |
| 1        | 0.691   | 0.2629    |
| 2        | 1.414   | 0.3809    |
| 10       | 6.723   | 0.4734    |
| 50       | 33.07   | 0.5020    |

### cubic

It is not clear how to expose a set of coefficients for the cubic method. The method requires a linear solve in each dimension to determine the
derivative at each point. A coefficient-caching implementation is probably not possible with the existing
methods.  The existing implementation uses every point in the model to compute the derivatives, so a large number of coefficients is potentially
required. There is an algorithm that requires 64 points [1], provided that table values and derivatives are available, however, it is not clear
whether it provides the same second derivative continuity as the current cubic method.

## Final Note on the Existing Methods

Benchmarking has made clear that we need to vectorize the existing flexible table methods. This will be a considerable refactor, and will help
to bridge the performance gap compared to the new fixed-table methods.

## References

1. Francois Lekien and Jerrold E. Marsden. "Tricubic interpolation in three dimensions." International Journal for Numerical Methods in Engineering,
   vol.64, 2005, pp. 455-471.
