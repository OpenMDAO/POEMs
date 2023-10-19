POEM ID: 077  
Title:  Derivative checks with multiple step sizes  
authors: kejacobson (Kevin Jacobson)  
Competing POEMs:  
Related POEMs: 076  
Associated implementation PR: [#2927](https://github.com/OpenMDAO/OpenMDAO/pull/2927)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

For models where complex step checks are not possible,
performing finite difference checks with multiple perturbation sizes is preferred to ensure
you are not "getting lucky" when comparing to a single real-valued finite difference step size.
Calling a separate `check_totals` or `check_partials` for each step size means
a duplicate evaluation of the analytical derivative for each step size.
For expensive models like CFD-based mutiphysics models, each duplicate evaluation can be hours of
wasted compute time.
The following example loops over 3 finite difference step sizes and calls `compute_jacvec_product`
3 times in fwd model.


```python
import openmdao.api as om

class Comp(om.ExplicitComponent):
    def setup(self):
        self.add_input('in')
        self.add_output('out')

    def compute(self, inputs, outputs):
        outputs['out'] = 2.0 * inputs['in'] ** 2.0

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'out' in d_outputs:
                if 'in' in d_inputs:
                    d_outputs['out'] += 4.0 * d_inputs['in'] * inputs['in']
        if mode == 'rev':
            if 'out' in d_outputs:
                if 'in' in d_inputs:
                    d_inputs['in'] += 4.0 * d_outputs['out'] * inputs['in']

def main():
    prob = om.Problem()
    prob.model.add_subsystem('ivc', om.IndepVarComp('in', 2))
    prob.model.add_subsystem('comp', Comp())
    prob.model.connect('ivc.in','comp.in')
    prob.setup()
    prob.run_model()

    step_sizes = [1e-5,1e-6,1e-7]
    for step in step_sizes:
        prob.check_totals(of='comp.out',wrt='ivc.in',step=step)

    # POEM 077 proposed version
    #prob.check_totals(of='comp.out',wrt='ivc.in',step=step_sizes)

if __name__ == '__main__':
    main()
```

## Description

The current POEM is proposing to allow a list of floats for the `step` option in `check_partials` and `check_totals` as
shown in the commented out version of the `check_totals` above.
One potential way to communicate the results to the screen is to print each step size in order after the analytic results
as shown below.

```

  Full Model: 'comp.out' wrt 'ivc.in'
    Analytic Magnitude: 8.000000e+00
          Fd Magnitude: 8.000002e+00 (fd:None)
    Absolute Error (Jan - Jfd) : 2.001412e-06 *

    Relative Error (Jan - Jfd) / Jfd : 2.501765e-07

    Raw Analytic Derivative (Jfor)
[[8.]]

    Raw FD Derivative (Jfd), step = 1e-5
[[8.000002]]

    Raw FD Derivative (Jfd), step = 1e-6
[[8.000002]]

    Raw FD Derivative (Jfd), step = 1e-7
[[8.00000018]]
```

For compact print, a new column with the step value could be added as a new column:


```
-----------------
Total Derivatives
-----------------

'<output>'                     wrt '<variable>'                   | step | calc mag.  | check mag. | a(cal-chk) | r(cal-chk)
----------------------------------------------------------------------------------------------------------------------------

'comp.out'                     wrt 'ivc.in'                       | 1e-5 | 8.0000e+00 | 8.0000e+00 | 2.0000e-05 | 2.5000e-06 >ABS_TOL >REL_TOL
'comp.out'                     wrt 'ivc.in'                       | 1e-6 | 8.0000e+00 | 8.0000e+00 | 2.0014e-06 | 2.5018e-07 >ABS_TOL
'comp.out'                     wrt 'ivc.in'                       | 1e-7 | 8.0000e+00 | 8.0000e+00 | 1.7881e-07 | 2.2352e-08
```
