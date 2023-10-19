POEM ID: 075  
Title: Convention for distributed/serial variables and when to allreduce  
authors: kejacobson (Kevin Jacobson)  
Competing POEMs: N/A  
Related POEMs: 046  
Associated implementation PR: [PR 2751](https://github.com/OpenMDAO/OpenMDAO/pull/2751)   


Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>

## Motivation

When computing reverse mode derivatives with components that involve a mix of serial
and distributed inputs and outputs, an allreduce on the component developer's side is required.
There are two possible places for the component developer to
put this allreduce to get the correct total derivatives. For MPhys, we had different
collaborators use the two different places which created incorrect derivatives when
coupling the codes (doing the allreduce in both places scaled the derivatives by n_proc).

We would like to establish a single convention for OpenMDAO parallel applications and test that the convention
is followed during `check_partials`.

## Description

### Representative Problem

The following code is an simplified version of a parallel flow solver workflow.
It contains a serial-in serial-out component,
a serial-in distributed-out component (representing the flow solver),
a distributed-in distributed-out component (component to integrate distributed surface forces),
and a distributed-in serial-out component (compute lift from distributed forces).
Ultimately, we want to compute derivatives of the serial output wrt the serial input.

The `current_om_convention` option switches between the two possible conventions for where the allreduce
can be added.

```python
import numpy as np
import openmdao.api as om
from mpi4py import MPI

dist_shape = 1 if MPI.COMM_WORLD.rank > 0 else 2

current_om_convention = False

class SerialComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('dv')
        self.add_output('aoa_serial')

    def compute(self, inputs, outputs):
        outputs['aoa_serial'] = 2.0* inputs['dv']

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'aoa_serial' in d_outputs:
                if 'dv' in d_inputs:
                    d_outputs['aoa_serial'] += 2.0 * d_inputs['dv']
        if mode == 'rev':
            if 'aoa_serial' in d_outputs:
                if 'dv' in d_inputs:
                    d_inputs['dv'] += 2.0 * d_outputs['aoa_serial']

class MixedSerialInComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('aoa_serial')
        self.add_output('flow_state_dist', shape = dist_shape, distributed=True)

    def compute(self, inputs, outputs):
        outputs['flow_state_dist'][:] = 0.5 * inputs['aoa_serial']

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'flow_state_dist' in d_outputs:
                if 'aoa_serial' in d_inputs:
                    d_outputs['flow_state_dist'] += 0.5 * d_inputs['aoa_serial']
        if mode == 'rev':
            if 'flow_state_dist' in d_outputs:
                if 'aoa_serial' in d_inputs:
                    if current_om_convention:
                        d_inputs['aoa_serial'] += 0.5 * np.sum(d_outputs['flow_state_dist'])
                    else:
                        d_inputs['aoa_serial'] += 0.5 * self.comm.allreduce(np.sum(d_outputs['flow_state_dist']))

class MixedSerialOutComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('aoa_serial')
        self.add_input('force_dist', shape = dist_shape, distributed=True)
        self.add_output('lift_serial')

    def compute(self, inputs, outputs):
        outputs['lift_serial'] = 2.0 * inputs['aoa_serial'] + self.comm.allreduce(3.0 * np.sum(inputs['force_dist']))

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'lift_serial' in d_outputs:
                if 'aoa_serial' in d_inputs:
                    d_outputs['lift_serial'] += 2.0 * d_inputs['aoa_serial']
                if 'force_dist' in d_inputs:
                    d_outputs['lift_serial'] += 3.0 * self.comm.allreduce(np.sum(d_inputs['force_dist']))
        if mode == 'rev':
            if 'lift_serial' in d_outputs:
                if 'aoa_serial' in d_inputs:
                    d_inputs['aoa_serial'] += 2.0 * d_outputs['lift_serial']
                if 'force_dist' in d_inputs:
                    if current_om_convention:
                        d_inputs['force_dist'] += 3.0 * self.comm.allreduce(d_outputs['lift_serial'])
                    else:
                        d_inputs['force_dist'] += 3.0 * d_outputs['lift_serial']

class DistComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('flow_state_dist', shape = dist_shape, distributed=True)
        self.add_output('force_dist', shape = dist_shape, distributed=True)

    def compute(self, inputs, outputs):
        outputs['force_dist'] = 3.0 * inputs['flow_state_dist']

    def compute_jacvec_product(self, inputs, d_inputs, d_outputs, mode):
        if mode == 'fwd':
            if 'force_dist' in d_outputs:
                if 'flow_state_dist' in d_inputs:
                    d_outputs['force_dist'] += 3.0 * d_inputs['flow_state_dist']
        if mode == 'rev':
            if 'force_dist' in d_outputs:
                if 'flow_state_dist' in d_inputs:
                    d_inputs['flow_state_dist'] += 3.0 * d_outputs['force_dist']

def create_problem():
    prob = om.Problem()
    model = prob.model
    ivc = om.IndepVarComp()
    ivc.add_output('dv', val = 1.0)

    model.add_subsystem('ivc', ivc)

    model.add_subsystem('serial_comp', SerialComp())
    model.add_subsystem('mixed_in_comp', MixedSerialInComp())
    model.add_subsystem('dist_comp', DistComp())
    model.add_subsystem('mixed_out_comp', MixedSerialOutComp())
    model.connect('ivc.dv', 'serial_comp.dv')
    model.connect('serial_comp.aoa_serial','mixed_in_comp.aoa_serial')
    model.connect('mixed_in_comp.flow_state_dist', 'dist_comp.flow_state_dist')
    model.connect('dist_comp.force_dist', 'mixed_out_comp.force_dist')
    model.connect('serial_comp.aoa_serial', 'mixed_out_comp.aoa_serial')
    return prob


def main():
    prob = create_problem()
    prob.setup(mode='rev')
    prob.run_driver()
    prob.check_partials()
    prob.check_totals(of='mixed_out_comp.lift_serial', wrt='ivc.dv')

if __name__ == '__main__':
    main()
```

### OpenMDAO Convention

The current OpenMDAO convention is based on the [theory](https://openmdao.org/newdocs/versions/latest/theory_manual/mpi.html) for ParallelGroups where the components are independent and distributed.
The `allreduce` is added to the partial term for the distributed input and serial output (the lift computer).
This creates correct partials and total derivatives with any number of processors with current OpenMDAO.

### Proposed Convention

__Proposed Rule: Serial inputs are the same value across all ranks of the component's comm;__
__therefore, corresponding reverse mode variables (d_input) should have the same value across all ranks of the component's comm.__

Following this rule, the allreduce goes in the component that has serial input and distributed output (the fake flow solver).
If a component has serial inputs and distributed outputs, the component developer is responsible for ensuring the serial reverse mode state is the same across the component's comm.
The derivatives wrt serial variables are correct with this approach, but analytic partials and totals when the `wrt` is a distributed variable are off by a factor of `n_proc`.

The benefits of this convention are:

1. This is how parallel solvers are written outside of OpenMDAO. When a user asks a flow solver for the derivative wrt angle of attack, the solver will internally perform an allreduce or something like it to make sure the user sees the same AoA derivative on each rank.
Conceptually, a user of a physics solver never cares about a rank's contribution to an angle of attack sensitivity or other serial variable, just the net sensitivity.
Same with a structural solver and derivatives with respect to panel thickness or geometry parameters.

2. Intermediate reverse mode states (adjoint vectors) are independent of the number of processors used with this convention.
This is helpful because these intermediate states are used for visualization such as [figure 10 of this paper](https://arc.aiaa.org/doi/full/10.2514/1.C032189).

3. When debugging, printing derivatives such as those wrt serial variables will be consistent across ranks.

### "Fixing" distributed variable derivatives in OpenMDAO for the new convention

For the final step of computing a derivative, OpenMDAO is doing an allreduce and division by number of processors. This should still be required for ParallelGroup cases and serial variables, but if the `wrt` variable is distributed, these steps should be skipped. I.e., OpenMDAO should add something like `if not variable.distributed` around this final allreduce+division step.

### Proposed test to ensure new convention is followed

When computing a check_totals or check_partials wrt a serial variable, OpenMDAO should check that the derivative is the same across all ranks.
If not, the component developer did not follow the proposed convention.

__NOTE: Enforcing this convention creates a backwards incompatibility for any users that wrote distributed models using the convention of putting the allreduce in the distributed input + serial output component.__
These users would see failing `check_partials` for mixed serial/distributed components if run in parallel.
They would also get incorrect analytic total derivatives if the `wrt` is distributed; the totals would be off by a factor of the number of processors.
