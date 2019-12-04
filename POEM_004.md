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
==========

Community feedback on spline component usage from Garett Barter (NREL) and Andrew Ning highlighted a few shortcomings of the current implementation.

* The current implementation requires a user to create a different Component for each interpolator even if they use the same control point and interpolated point locations.
* The API between the two currently implemented spline components (AkimaSplineComp, BsplineComp) significantly diverges.
* The interpolation algorithms should be available for standalone use.
* The interpolater implementations in the spline components (in particular Akima) are separate from those in the StructuredMetaModel Component and should be combined to eliminate code duplication.

Please see the reference section for links to the current implementation.

Description
===========

This POEM seeks to integrate `AkimaSplineComp` and `BsplineComp` into a single spline component with an API that is consistent with the two meta model components ([StructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelstructured_comp.html),  [UnstructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelunstructured_comp.html) as of 2.9.1).

The fundamental difference between the proposed `SplineComp` and the existing `StructuredMetaModelComp` are as follows:

* `StructuredMetaModel` is used when the user has a known set of x and y training points on a structured grid and wants to interpolate a new y value at a new x location that lies between those points. For this component, the user needs an array of training points for each input and output dimension; generally, these remain constant. `StructuredMetaModel` can be used for multi dimensional design spaces, whereas `SplineComp` is restricted to one input.

* `SplineComp` is used when a user wants to represent a large dimensional variable as a smaller dimensional variable. The smaller dimension is represented by its x and y values which are called control points. The larger dimension consists of the interpolated points. Typically the x location of the control points and the interpolated points is known, and the y value at the interpolated point is calculated for each new y at the control point. 

With these difference in mind, we crafted the new SplineComp API to have a similar workflow to the StructuredMetaModel Component. 

SplineComp API
--------------------
```
    class SplineComp(ExplicitComponent):
```

Below are the signatures of the proposed class:

```
    def __init__(self, method, x_cp_val, x_interp, x_cp_name='x_cp', x_interp_name='x_interp',
                 x_units=None, vec_size=1, interp_options={}):
        """
        Initialize all attributes.

        Parameters
        ----------
        method : str
            Interpolation method. Valid values are ['akima', 'bspline', (more to come)]
        x_cp_val : list or ndarray
            List/array of x control point values, must be monotonically increasing.
        x_interp : list or ndarray
            List/array of x interpolated point values.
        x_cp_name : str
            Name for the x control points input.
        x_interp_name : str
            Name of the x interpolated points input.
        x_units : str or None
            Units of the x variable.
        vec_size : int
            The number of independent splines to interpolate.
        interp_options : dict
            Dict contains the name and value of options specific to the chosen interpolation method.
        """
```

```
    def add_spline(self, y_cp_name, y_interp_name, y_cp_val=None, y_units=None):
        """
        Add a single spline output to this component.

        Parameters
        ----------
        y_cp_name : str
            Name for the y control points input.
        y_interp_name : str
            Name of the y interpolated points output.
        y_cp_val : list or ndarray
            List/array of default y control point values.
        y_units : str or None
            Units of the y variable.
        """
```

Simple Example of SplineComp API
---------------------------------

Suppose a user has a set of points that describe a curve. In our example we are trying to generate interpolated points between our control points. To set the x position of control points in `SplineComp` we pass `x_cp` into `x_control_points` and pass `x` into `x_interp` to set the position of points we would like to interpolate at (Figure 1). Now, we will pass in the y position of the control points `y_cp` into `y_control_points` through the `add_spline` method (Figure 2). `SplineComp` calculates the `y_interp` values and gives the output of interpolated points (Figure 3).

**Single Spline Example of Proposed API**
```
    # Data
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 20)

    prob = om.Problem()

    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x)
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_cp_name='y_val', y_interp_name='y_val', y_cp_val=y_cp)

    y_interp = prob['akima1.y_val']
```


![step1](POEM_004/figure_1.png)

![step2](POEM_004/figure_2.png) 

![step3](POEM_004/figure_3.png) 

![step4](POEM_004/figure_4.png) 

Further Examples
----------------
Next are a few examples of what the proposed API looks like for a few specific cases:

**Multiple Splines, One Interpolant Method Example**  
Each spline you add will use the same `x_cp_val`, `x_interp`, and `method` arguments.  
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x, x_interp_name='x_val')
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_cp_name='ycp1', y_interp_name='y_val1', y_cp_val=y_cp)
    comp.add_spline(y_cp_name='ycp2', y_interp_name='y_val2', y_cp_val=y_cp2)

    y_interp = prob['akima1.y_val1']
```

**Passing Optional Arguments To Akima**  
In this example we are passing in `delta_x` and `eps` which are specific to the akima method.
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    akima_option = {'delta_x': 0.2, 'eps': 1e-30}
    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', 
                         x_interp_name='x_val',  x_units='km', interp_options=akima_options)

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_cp_name='alt_cp', y_interp_name='alt', y_cp_val=y_cp, y_units='kft')

    y_interp_spline1 = prob['atmosphere.alt']
```

**Passing Optional Arguments To BSpline**
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0]]) / 12.0
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    bspline_options = {'order': 5}
    comp = om.SplineComp(method='bspline', x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', 
                         x_interp_name, x_interp_name='x_val', x_units='km', 
                         interp_options=bspline_options)

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_cp_name='temp_cp', y_interp_name='temp', y_cp_val=y_cp2, y_units='C')

    y_interp_spline1 = prob['atmosphere.temp']
```

Standalone usage of the interpolants
------------------------------------
See message from Ken


Backwards Incompatible Changes From 2.9.1
------------------------------------------

Removing distribution argument from spline comp.

In the new SplineComp, the following options are not preserved: 
* `distribution` from BsplinesComp
* `eval_at` from AkimaSplineComp

These options are being removed in favor of requiring the user to specify the x locations of the control point and interpolated points. However, we are open for discussion on preserving the capability in some way, such as a helper library or additional API functions.

Renaming StructuredMetaModel
-----------------------------

We are considering changing the name of StructuredMetaModelComp to InterpNdComp (or InterpNDComp) to differentiate it from UnstructuredMetaModelComp.

References
-----------
1. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/akima_spline_comp.html
2. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/bsplines_comp.html


