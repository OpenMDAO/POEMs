POEM ID:  004  
Title:   Creating Interpolant Class For 1D Splines  
authors: [DKilkenny]  
Competing POEMs: [N/A]  
Related POEMs: [N/A]  
Associated Implementation PR:

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

Community feedback on spline component usage from Garett Barter (NREL) and Andrew Ning

The current implementation requires a user to create a different component for each interpolator. In addition, the API between the two components significantly diverge. Please see the reference section for links to the current implementation.


Description
-----------

This POEM seeks to integrate `akima_spline_comp` and `bspline_comp` into a single spline component with an API that is self consistent with the two meta model components ([StructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelstructured_comp.html),  [UnstructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelunstructured_comp.html) as of 2.9.1).

First, we will talk about the difference between the new `SplineComp` and existing `StructuredMetaModelComp`.

* `StructuredMetaModel` is used when the user has a known set of x and y training points and want to interpolate between those training points. For this component, the user will need an array of training points for each `add_input` and `add_output` that they will add to the component. `StructuredMetaModel` is used for multi dimentional design spaces where as `SplineComp` is used for 1D splines.

* `SplineComp` is used when a user has the coefficients (*control points*) of a regression line and want to interpolate at *N* points. To do this, a user needs three things: `x_control_points`, `y_control_points`, and `x_interp`. With this information, `SplineComp` calculates the y value of each `x_interp` value to give. This is helpful if you do not have any training data but need an interpolated spline between the regression line coefficients (*control points*). 

Next we'll show an example of when `SplineComp` would be used.

Suppose a user has a set of points that describe a curve. In our example we are trying to generate interpolated points between our control points. To set the x position of control points in `SplineComp` we pass `x_cp` into `x_control_points` and pass `x` into `x_interp` to set the position of points we would like to interpolate at (Figure 1). Now, we will pass in the y position of the control points `y_cp` into `y_control_points` through the `add_spline` method (Figure 2). `SplineComp` calculates the `y_interp` values and gives the output of interpolated points (Figure 3).

**Single Spline Example of Proposed API**
```
    # Data
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 20)

    prob = om.Problem()

    comp = om.SplineComp(x_cp_val=x_cp, x_interp=x, x_interp_name='x_val', method='akima')
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_interp_name='y_val', y_cp_val=y_cp)

    y_interp = prob['akima1.y_val']
```


![step1](figure_1.png)

![step2](figure_2.png) 

![step3](figure_3.png) 

![step4](figure_4.png) 


SplineComp API
--------------------
```
    class SplineComp(ExplicitComponent):
```

Below are the signatures of the proposed class:

```
    def __init__(self, x_cp_val, x_interp, x_cp_name=None, x_interp_name=None, method=None,
                 axis_units=None, vec_size=1):
```

```
    def add_spline(self, y_interp_name, y_cp_name=None, y_cp_val=None, axis_units=None, **kwargs):
```

Next are a few examples of what the proposed API might look like:


**Multiple Splines, One Interpolant Method Example**  
Each spline you add will use the same `x_cp_val`, `x_interp`, and `default_method` arguments.  
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    comp = om.SplineComp(x_cp_val=x_cp, x_interp=x, x_interp_name='x_val', method='akima')
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_interp_name='y_val1', y_cp_val=y_cp)
    comp.add_spline(y_interp_name='y_val2', y_cp_val=y_cp2)

    y_interp = prob['akima1.y_val1']

    print(y_interp)
    print(prob['akima1.x_val'])
```

**Passing Optional Arguments To Akima**
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    comp = om.SplineComp(x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', 
                         x_interp_name='x_val', method='akima', axis_units='km')

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_interp_name='alt', y_cp_name='alt_cp', y_cp_val=y_cp, 
                    axis_units='kft', delta_x=0.2, eps=1e-30)

    y_interp_spline1 = prob['atmosphere.alt']

    print(y_interp_spline1)
```

**Passing Optional Arguments To BSpline**
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    comp = om.SplineComp(x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', x_interp_name='x_val', 
                         method='bspline', axis_units='km')

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_interp_name='temp', y_cp_name='temp_cp', y_cp_val=y_cp2, axis_units='C', 
                    order=5)

    y_interp_spline1 = prob['atmosphere.temp']

    print(y_interp_spline1)
```

Backwards Incompatible Changes From 2.9.1
------------------------------------------

Removing distribution argument from spline comp.

* We are removing both `distribution` and `eval_at` component options because they were both specifying a distribution of control points on the spline. These two are being replaced with the `x_cp_val` option. Grid input distribution helper functions will be added to provide distributed control points to the class. This can be seen below using the *Single Spline Example* case

```
    from openmdao.components.SplineInterpDistributions import sin_dist
    # Data
    x_cp = sin_dist(np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]))
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 20)

    prob = om.Problem()

    comp = om.SplineComp(x_cp_val=x_cp, x_interp=x, x_interp_name='x_val', method='akima')
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_interp_name='y_val', y_cp_val=y_cp)

    y_interp = prob['akima1.y_val']
```

* While we are looking to remove `distribution` and `eval_at`, we are preserving `delta_x`, `eps`, and `order` and they will still be passable to their respective interpolation methods. (Depending on how we decide to input the spline method specific kwargs this might change)

Renaming StructuredMetaModel
-----------------------------

Because `StructuredMetaModel` can interpolate for more than one dimension, we think it is appropriate to rename the `StructuredMetaModel` component to `InterpNdComp`. We will apply a deprecation warning to StructuredMetaModel in the PR associated with this.

References
-----------
1. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/akima_spline_comp.html
2. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/bsplines_comp.html


