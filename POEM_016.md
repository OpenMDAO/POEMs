POEM ID: 016  
Title: Linear algebra components can perform multiple calculations.  
authors: robfalck (Rob Falck)  
Competing POEMs: None  
Related POEMs: None  
Associated implementation PR: None  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------
The current linear algebra components (MatrixVectorProductComp, DotProductComp) perform a single
matrix vector multiplication or dot product, respectively.  There are often situations when numerous
matrix vector products need to be computed, essentially in parallel.

```
accel_a = M_ba * accel_b + M_ga * accel_g + M_ga * vr
```

To reduce the complexity of models, we are proposing to allow the MatrixVectorProductComp, DotProductComp,  
CrossProductComp, and VectorMagnitudeComp components to calculate multiple products/magnitudes.

Description
-----------

API Changes:

1. MatrixVectorProductComp, DotProductComp, and CrossProductComp have a new method `add_product` which has a slightly different set of arguments for each commponent.

```
class MatrixVectorProductComp

    def add_product(output, matrix, vector, output_units=None, matrix_units=None, vector_units=None, vec_size=1, shape=(3, 3))
        """
        Adds a new output product to the matrix vector product component.
        
        Parameters
        ----------
        output : str
            The name of the vector product output.
        matrix : str
            The name of the matrix input.
        vector : str
            The name of the vector input.
        output_units : str or None
            The units of the output matrix.
        matrix_units : str or None
            The units of the input matrix.
        vector_units : str or None
            The units of the input vector.
        vec_size : int
            The number of points at which the matrix vector product
            should be computed simultaneously.
        shape : tuple of (int, int)
            The shape of the matrix at each point.  The first element
            also specifies the size of the output at each point.  The
            second element specifies the size of the input vector at
            each point.  For example, if vec_size=10 and shape is (5, 3),
            then the input matrix will have a shape of (10, 5, 3), the
            input vector will have a shape of (10, 3), and the output
            vector will have shape of (10, 5).
        """
```

Internally, MatrixVectorProductComp should keep track of the variable names
added with each `add_product` call.  Thus if we use variable name `M_ga` in
multiple products, it is only a single input to the component. If variable
names are used in multiple calls to `add_product`, some checking will be necessary:
- An input name in one call to `add_product` may not be an output name in another call, and vice-versa.
- The units and shape of variables used across multiple products must be the same in each one.

```
class DotProductComp

    def add_product(output, a, b, output_units=None, a_units=None, b_units=None, vec_size=1, length=3)
        """
        Adds a new output product to the dot product component.
        
        Parameters
        ----------
        output : str
            The name of the vector product output.
        a : str
            The name of the first vector input.
        b : str
            The name of the second input.
        output_units : str or None
            The units of the output.
        a_units : str or None
            The units of input a.
        b_units : str or None
            The units of input b.
        vec_size : int
            The number of points at which the dot vector product
            should be computed simultaneously.  The shape of
            the output is (vec_size,).
        length : int
            The length of the vectors a and b.  Their shapes are
            (vec_size, length)
        """
```

The same rules for variable caching and shape/unit consistency that
apply to MatrixVectorProductComp apply here.

```
class CrossProductComp

    def add_product(output, a, b, output_units=None, a_units=None, b_units=None, vec_size=1)
        """
        Adds a new output product to the cross product component.  Computes
        
        output = a x b where output, a, and b are all sized as (vec_size, 3).
        
        Parameters
        ----------
        output : str
            The name of the vector product output.
        a : str
            The name of the first vector input.
        b : str
            The name of the second input.
        output_units : str or None
            The units of the output.
        a_units : str or None
            The units of input a.
        b_units : str or None
            The units of input b.
        vec_size : int
            The number of points at which the dot vector product
            should be computed simultaneously.  The shape of
            the output is (vec_size,).
        """
```

The same rules for variable caching and shape/unit consistency that
apply to MatrixVectorProductComp apply here.

```
class VectorMagnitudeComp

    def add_magnitude(mag_name, in_name=None, units=None, vec_size=1)
        """
        Adds a new vector magnitude to be computed by the VectorMagnitudeComp.
        
        Parameters
        ----------
        mag_name : str
            The name of the vector magnitude.
        in_name : str
            The name of the vector input.
        units : str or None
            The units of input and vector and its magnitude.
        vec_size : int
            The number of points at which the vector magnitude
            should be computed simultaneously.  The shape of
            the input is (vec_size, length) and output is (vec_size,).
        length : int
            The length of the input vector whose magnitude is to be computed.
        """
```
