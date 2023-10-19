POEM ID: 076  
Title:  Directional total derivative checks  
authors: kejacobson (Kevin Jacobson)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2859](https://github.com/OpenMDAO/OpenMDAO/pull/2859)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation

When performing a `check_totals` for arrays of design variables,
OpenMDAO will perform a finite difference for each element of the design variable array.
For expensive models with large design variable arrays, such as a finite element model
with 100s or 1000s of design variables, `check_totals` is not useful because it's too slow.
Our current workaround is to manually perform total checks for a handful DVs 
with a finite difference of `run_model` compared to `compute_totals` or manually
do a directional derivative check.

```python
import numpy as np
import openmdao.api as om

class Comp(om.ExplicitComponent):
    def setup(self):
        self.add_input('in', shape=10)
        self.add_output('out')

    def compute(self, inputs, outputs):
        print('compute')
        outputs['out'] = np.sum(inputs['in'])

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'out' in d_outputs:
                if 'in' in d_inputs:
                    print('fwd')
                    d_outputs['out'] += np.sum(d_inputs['in'])
        if mode == 'rev':
            if 'out' in d_outputs:
                if 'in' in d_inputs:
                    print('rev')
                    d_inputs['in'] += d_outputs['out']

def main():
    prob = om.Problem()
    ivc = om.IndepVarComp()
    ivc.add_output('in', np.arange(10))
    prob.model.add_subsystem('ivc', ivc)

    prob.model.add_subsystem('comp', Comp())
    prob.model.connect('ivc.in','comp.in')
    prob.setup(mode='rev')
    prob.run_model()

    prob.check_totals(of='comp.out',wrt='ivc.in')

if __name__ == '__main__':
    main()
```

## Description

The current POEM is proposing an bool option `directional` be added to `check_totals`, where
OpenMDAO will perform a single finite difference check perturbing all the variables specified in `wrt` 
with a random seed/direction vector.

```python
# perform a single finite difference perturbation.
prob.check_totals(of='comp.out',wrt='ivc.in', directional=True)

# Could specify multiple wrt variables and still perform a single perturbed model evaluation
prob.check_totals(of='mass',wrt=['struct_dvs', 'aero_dvs'], directional=True)
```
