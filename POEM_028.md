POEM ID:  028
Title: check_partials input warnings  
authors: [@ehariton] (Eliot Aretskin-Hariton)   
Competing POEMs: N/A  
Related POEMs: N/A 
Associated implementation PR:   

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------


`check_partials()` and `assert_check_partials()` are often used in ExplicitComponents to ensure that the derivatives are correct. 
However, these partial derivative checks rely on the starting input point of the model.
Thus, if the user does not choose good values for this initial point, the partial checks will pass even if the partials are incorrect.
This will lead to lack of convergence when this component is integrated into the larger problem.
Typical input values that can cause non-convergence are input values set to 0 or 1.
It should also be noted that the default value for inputs is 1.
This creates opportunities for bad derivatives to sneak into a large optimization.


Description
-----------


`check_partials()` and `assert_check_partials()` passes even though partial derivatives are incorrect in some cases.

Example Code:
```
import openmdao.api as om

class Line(om.ExplicitComponent):

    def setup(self):

        # Inputs
        self.add_input('m', val=0.0, units=None,)
        self.add_input('X', val=1.0, units='m',)
        self.add_input('b', val=1.0, units='m',)

        self.add_output('Y', val=0.0, units='m')

        self.declare_partials('Y',['m','X','b'])


    def compute(self, inputs, outputs):
        m = inputs['m']
        X = inputs['X']
        b = inputs['b']

        outputs['Y'] = m * X + b

    def compute_partials(self, inputs, partials):
        m = inputs['m']
        X = inputs['X']
        b = inputs['b']

        partials['Y', 'X'] = 2*m  # this partial is wrong
        partials['Y', 'm'] = X**2 # this partial is wrong
        partials['Y', 'b'] = 1.0


if __name__ == '__main__':

    p = om.Problem()
    p.model = om.Group()

    p.model.add_subsystem('Line', Line(), promotes=['*'])

    p.setup(check=False, force_alloc_complex=True)
    p.check_partials(compact_print=True, method='cs')
    
    p.setup()
    p.run_model()
```
Results:
```
Component: Line 'Line'
'<output>' wrt '<variable>' | fwd mag.   | check mag. | a(fwd-chk) | r(fwd-chk)
-------------------------------------------------------------------------------

'Y'        wrt 'X'          | 0.0000e+00 | 0.0000e+00 | 0.0000e+00 | nan
'Y'        wrt 'b'          | 1.0000e+00 | 1.0000e+00 | 0.0000e+00 | 0.0000e+00
'Y'        wrt 'm'          | 1.0000e+00 | 1.0000e+00 | 0.0000e+00 | 0.0000e+00
```


References
-----------

1. http://openmdao.org/twodocs/versions/3.0.0/features/core_features/working_with_derivatives/check_partials_subset.html?highlight=check_partials
2. http://openmdao.org/twodocs/versions/3.0.0/features/core_features/working_with_derivatives/unit_testing_partials.html?highlight=assert_check_partials


Poem: The Squiggly Map
-----------


Zero and One  
what have you done?  
I follow your map  
though it's surely a trap.  
Each step that I take  
leads away from the lake.  
And for water I'm desperately seeking.  