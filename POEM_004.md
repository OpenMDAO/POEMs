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

Community feedback on spline component usage from Garett Barter (NREL) and Andrew Ning (BYU) highlighted a few shortcomings of the current implementation.

* The current implementation requires a user to create a different Component for each interpolator even if they use the same control point and interpolated point locations.
* The API between the two currently implemented spline components (`AkimaSplineComp`, `BsplineComp`) significantly diverges.
* The interpolation algorithms should be available for standalone use.
* The interpolator implementations in the spline components (in particular Akima) are separate from those in the StructuredMetaModel Component and should be combined to eliminate code duplication.

Please see the reference section for links to the current implementation.

Description
===========

This POEM seeks to integrate `AkimaSplineComp` and `BsplineComp` into a single spline component with an API that is consistent with the two meta model components ([StructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelstructured_comp.html),  [UnstructuredMetaModel](http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/metamodelunstructured_comp.html) as of 2.9.1). Additionally, it will also unify the underlying interpolation routines between `AkimaSplineComp` and `StructuredMetaModel` and define an API for them to be used independently of the components themselves. 

The fundamental difference between the proposed `SplineComp` and the existing `StructuredMetaModelComp` are as follows:

* `StructuredMetaModel` is used when the user has a known set of x and y training points on a structured grid and wants to interpolate a new y value at a new x location that lies between those points. For this component, the user needs an array of training points for each input and output dimension; generally, these remain constant. `StructuredMetaModel` can be used for multi-dimensional design spaces, whereas `SplineComp` is restricted to one input.

* `SplineComp` is used when a user wants to interpolate to a large array of values from a small array of control points. The smaller control points are defined by their x and y values. Typically, the x location of the control points and the interpolated points are known a priori, and the y value at the interpolated point is calculated for each new y at the control point. 

With these difference in mind, we crafted the new SplineComp API to have a similar workflow to the StructuredMetaModel Component. 

SplineComp API
--------------------
```
    class SplineComp(ExplicitComponent):

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

Example Usage of SplineComp API
---------------------------------

Suppose a user has a set of points that describe a curve. In our example we are trying to generate interpolated points between our control points. To set the x position of control points in `SplineComp` we pass `x_cp` into `x_cp_val` and pass `x` into `x_interp` to set the position of points we would like to interpolate at (Figure 1). Now, we will pass in the y position of the control points `y_cp` into `y_cp_val` through the `add_spline` method (Figure 2). `SplineComp` calculates the `y_interp` values and gives the output of interpolated points (Figure 3).

**Single Spline Example of Proposed API**
```
    # Data
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0])
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 20)

    prob = om.Problem()

    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x)
    prob.model.add_subsystem('akima1', comp)

    comp.add_spline(y_cp_name='ycp', y_interp_name='y_val', y_cp_val=y_cp)

    y_interp = prob['akima1.y_val']
```


![step1](POEM_004/figure_1.png)

![step2](POEM_004/figure_2.png) 

![step3](POEM_004/figure_3.png) 

![step4](POEM_004/figure_4.png) 

Further Examples
----------------
Next are a few examples of what the proposed API looks like for a few specific cases:

**Multiple Splines, One Interpolant Method**  
Each spline you add will use the same `x_cp_val`, `x_interp`, and `method` arguments.  
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0])
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x, x_interp_name='x_val')
    prob.model.add_subsystem('akima_component', comp)

    comp.add_spline(y_cp_name='ycp1', y_interp_name='y_val1', y_cp_val=y_cp)
    comp.add_spline(y_cp_name='ycp2', y_interp_name='y_val2', y_cp_val=y_cp2)

    y_interp = prob['akima_component.y_val1']
```

**Passing Optional Arguments To Akima**  
In this example we are passing in `delta_x` and `eps` which are specific to the akima method.
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0])
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    akima_option = {'delta_x': 0.2, 'eps': 1e-30}
    comp = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', 
                         x_interp_name='x_val',  x_units='km', interp_options=akima_options)

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_cp_name='alt_cp', y_interp_name='alt', y_cp_val=y_cp, y_units='kft')

    y_interp = prob['atmosphere.alt']
```

**Passing Optional Arguments To BSpline**
```
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0])
    y_cp2 = np.array([1.0, 5.0, 7.0, 8.0, 13.0, 16.0])
    x = np.linspace(1.0, 12.0, 50)

    prob = om.Problem()

    bspline_options = {'order': 5}
    comp = om.SplineComp(method='bspline', x_cp_val=x_cp, x_interp=x, x_cp_name='xcp', 
                         x_interp_name='x_val', x_units='km', 
                         interp_options=bspline_options)

    prob.model.add_subsystem('atmosphere', comp)

    comp.add_spline(y_cp_name='temp_cp', y_interp_name='temp', y_cp_val=y_cp2, y_units='C')

    y_interp = prob['atmosphere.temp']
```

**Non-uniform Distributions Example**
```
    from openmdao.utils.spline_distributions import CellCentered, NodeCentered, SineDistribution
    x_cp = np.array([1.0, 2.0, 4.0, 6.0, 10.0, 12.0])
    y_cp = np.array([5.0, 12.0, 14.0, 16.0, 21.0, 29.0])
    x_cell_centered = CellCentered(xcp, num_points=20)
    x_node_centered = NodeCentered(xcp, num_points=20)
    x_sin_dist = SineDistribution(xcp, num_points=20)

    prob = om.Problem()

    comp1 = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x_cell_centered)
    comp2 = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x_node_centered)
    comp3 = om.SplineComp(method='akima', x_cp_val=x_cp, x_interp=x_sin_dist)

    prob.model.add_subsystem('akima1', comp1)
    prob.model.add_subsystem('akima2', comp2)
    prob.model.add_subsystem('akima3', comp3)

    comp1.add_spline(y_cp_name='ycp', y_interp_name='y_val', y_cp_val=y_cp)
    comp2.add_spline(y_cp_name='ycp', y_interp_name='y_val', y_cp_val=y_cp)
    comp3.add_spline(y_cp_name='ycp', y_interp_name='y_val', y_cp_val=y_cp)
```

Standalone Usage of The Interpolants
------------------------------------

We also propose a functional standalone interface for directly using any of the interpolants. 
```
    def interp(method, x_data, y_data, x):
        """
        Compute y and its derivatives for a given x by interpolating on x_data and y_data.
        Parameters
        ----------
        method : str
            Method to use, choose from all available openmmdao methods.
        x_data : ndarray or list
            Input data for x, should be monotonically increasing. For higher dimensional grids,
            x_data should be a list containing the x data for each dimension.
        y_data : ndarray
            Input values for y. For higher dimensional grids, the index order should be the same as
            in x_data.
        x : float or iterable or ndarray
            Location(s) at which to interpolate.
        Returns
        -------
        float or ndarray
            Interpolated values y
        ndarray
            Derivative of y with respect to x
        ndarray
            Derivative of y with respect to x_data
        ndarray
            Derivative of y with respect to y_data
        """
```
This simple standalone function is intended to be used for standard interpolation (`StructuredMetaModel`), including for multidimensional data sets, and for constructing a higher dimension curve from a low dimensional representation (`SplineComp`), as we use the spline components. This simplicity and flexibility comes at a small cost of some performance, particularly when using the 'b-spline' method, as we aren't pre-computing any values for use in subsequent calls. To do so would require independent APIs for standard interpolation and usage as a spline.

Usage looks like this where we want to compute new y for new x: 
```
    y, dy_dx, dy_dx_train, dy_dy_train = interp('akima', x_input, y_input, x)
```

API Changes From 2.9.1
------------------------------------------

Deprecation of `AkimaSplineComp` and `BsplineComp` and replacement with unified `SplineComp`. 


In the new SplineComp, the following options are not preserved: 
* `distribution` from BsplinesComp
* `eval_at` from AkimaSplineComp

These options are being removed in favor of requiring the user to specify the x locations of the control point and interpolated points. 
We will provide helper functions for the common uses cases (e.g. cell-centered, node-centered, sine/cosine distributions)

Renaming StructuredMetaModel
-----------------------------

We are considering changing the name of StructuredMetaModelComp to InterpNdComp (or InterpNDComp) to differentiate it from UnstructuredMetaModelComp.

References
-----------
1. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/akima_spline_comp.html
2. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/bsplines_comp.html


