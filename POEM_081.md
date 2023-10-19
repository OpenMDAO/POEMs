POEM ID: 081  
Title: Add Submodel Component to standard component set.  
authors: nsteffen (Nate Steffen)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2817](https://github.com/OpenMDAO/OpenMDAO/pull/2817)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [x] Integrated

## Motivation

Sometimes, the user might wish to set up a problem that has models that evaluate OpenMDAO systems themselves. However, there is currently no simple way to do this within OpenMDAO.

As the depth of a system increases, the input and output vectors can grow quite large. This increases the complexity of the interface and can slow its performance, and OpenMDAO doesn't have any mechanism to remedy this.

The current OpenMDAO API doesn't have an intuitive way of nesting drivers (wrapping a driver around a problem with a driver).

## Proposed Solution

A new submodel component will allow for a user to modularize their OpenMDAO systems. Not only can this "hide" certain inputs from the top-level model and reduce its input vector size, but it allows for OpenMDAO systems to be evaluated within an overall OpenMDAO system.

The code below is how the new subproblem component will look. Its inputs are similar to that of `Problem`, and since it is an `om.ExplicitComponent`, it can be added as a subsystem to a model in a top-level problem.

## Prototype Implementation
**NOTE:** Driver variables are not automatically respected and must be added manually in this implementation.

```python
"""Define the SubmodelComp class for evaluating OpenMDAO systems within components."""

from openmdao.core.constants import _SetupStatus, INF_BOUND
from openmdao.core.explicitcomponent import ExplicitComponent
from openmdao.utils.general_utils import find_matches
from openmdao.utils.reports_system import clear_reports


class SubmodelComp(ExplicitComponent):
    """
    System level container for systems.

    Parameters
    ----------
    problem : <Problem>
        Instantiated problem to use for the model.
    inputs : list of str or tuple or None
        List of provided input names in str or tuple form. If an element is a str,
        then it should be the promoted name in its group. If it is a tuple,
        then the first element should be the group's promoted name, and the
        second element should be the var name you wish to refer to it within the subproblem
        [e.g. (path.to.var, desired_name)].
    outputs : list of str or tuple or None
        List of provided output names in str or tuple form. If an element is a str,
        then it should be the promoted name in its group. If it is a tuple,
        then the first element should be the group's promoted name, and the
        second element should be the var name you wish to refer to it within the subproblem
        [e.g. (path.to.var, desired_name)].
    reports : bool
        Determines if reports should be include in subproblem. Default is False because
        submodelcomp runs faster without reports.
    **kwargs : named args
        All remaining named args that become options for `SubmodelComp`.

    Attributes
    ----------
    _subprob : <Problem>
        Instantiated problem used to run the model.
    submodel_inputs : list of tuple
        List of inputs requested by user to be used as inputs in the
        subproblem's system.
    submodel_outputs : list of tuple
        List of outputs requested by user to be used as outputs in the
        subproblem's system.
    """

    def __init__(self, problem, inputs=None, outputs=None, reports=False, **kwargs):
        """
        Initialize all attributes.
        """
        super().__init__(**kwargs)

        if not reports:
            clear_reports(problem)
        self._subprob = problem

        self.submodel_inputs = {}
        self.submodel_outputs = {}

        if inputs is not None:
            for inp in inputs:
                if isinstance(inp, str):
                    self.submodel_inputs[inp] = {'iface_name': inp.replace('.', ':')}
                elif isinstance(inp, tuple):
                    self.submodel_inputs[inp[0]] = {'iface_name': inp[1]}
                else:
                    raise Exception(f'Expected input of type str or tuple, got {type(inp)}.')

        if outputs is not None:
            for out in outputs:
                if isinstance(out, str):
                    self.submodel_outputs[out] = {'iface_name': out.replace('.', ':')}
                elif isinstance(out, tuple):
                    self.submodel_outputs[out[0]] = {'iface_name': out[1]}
                else:
                    raise Exception(f'Expected output of type str or tuple, got {type(out)}.')

    def add_input(self, path, name=None, **kwargs):
        """
        Add input to model before or after setup.

        Parameters
        ----------
        path : str
            Absolute path name of input.
        name : str or None
            Name of input to be added. If none, it will default to the var name after
            the last '.'.
        **kwargs : named args
            All remaining named args that can become options for `add_input`
        """
        if name is None:
            name = path.replace('.', ':')

        self.submodel_inputs[path] = {'iface_name': name, **kwargs}

        # if the submodel is not set up fully, then self._problem_meta will be None
        # in which case we only want to add inputs to self.submodel_inputs
        if not self._problem_meta:
            return

        if self._problem_meta['setup_status'] > _SetupStatus.POST_CONFIGURE:
            raise Exception('Cannot call add_input after configure.')

        meta = self.boundary_inputs[path]

        # if the user wants to change some meta data like val, units, etc. they can update it here
        for key, val in kwargs.items():
            meta[key] = val

        meta.pop('prom_name')
        super().add_input(name, **meta)
        meta['prom_name'] = path

    def add_output(self, path, name=None, **kwargs):
        """
        Add output to model before or after setup.

        Parameters
        ----------
        path : str
            Absolute path name of output.
        name : str or None
            Name of output to be added. If none, it will default to the var name after
            the last '.'.
        **kwargs : named args
            All remaining named args that can become options for `add_output`
        """
        if name is None:
            name = path.replace('.', ':')

        self.submodel_outputs[path] = {'iface_name': name, **kwargs}

        # if the submodel is not set up fully, then self._problem_meta will be None
        # in which case we only want to add outputs to self.submodel_outputs
        if not self._problem_meta:
            return

        if self._problem_meta['setup_status'] > _SetupStatus.POST_CONFIGURE:
            raise Exception('Cannot call add_output after configure.')

        meta = self.all_outputs[path]

        for key, val in kwargs.items():
            meta[key] = val

        meta.pop('prom_name')
        super().add_output(name, **meta)
        meta['prom_name'] = path

    def _reset_driver_vars(self):
        # NOTE driver var names can be different from those in model
        # this causes some problems, so this function is used to
        # reset the driver vars so the inner problem only uses
        # the model vars
        p = self._subprob

        p.driver._designvars = {}
        p.driver._cons = {}
        p.driver._objs = {}
        p.driver._responses = {}

    def setup(self):
        """
        Perform some final setup and checks.
        """
        p = self._subprob

        # if subprob.setup is called before the top problem setup, we can't rely
        # on using the problem meta data, so default to False
        if self._problem_meta is None:
            p.setup(force_alloc_complex=False)
        else:
            p.setup(force_alloc_complex=self._problem_meta['force_alloc_complex'])
        p.final_setup()

        self.boundary_inputs = {}
        indep_vars = p.list_indep_vars(out_stream=None)
        for name, meta in indep_vars:
            if name in p.model._var_abs2prom['input']:
                meta['prom_name'] = p.model._var_abs2prom['input'][name]
            elif name in p.model._var_abs2prom['output']:
                meta['prom_name'] = p.model._var_abs2prom['output'][name]
            elif p.model.get_source(name).startswith('_auto_ivc.'):
                meta['prom_name'] = name
            else:
                raise Exception(f'var {name} not in meta data')
            self.boundary_inputs[name] = meta

        self.all_outputs = {}
        outputs = p.model.list_outputs(out_stream=None, prom_name=True,
                                       units=True, shape=True, desc=True)

        # turn outputs into dict
        for _, meta in outputs:
            self.all_outputs[meta['prom_name']] = meta

        wildcard_inputs = [var for var, _ in self.submodel_inputs.items()
                           if '*' in var]
        wildcard_outputs = [var for var, _ in self.submodel_outputs.items()
                            if '*' in var]

        for inp in wildcard_inputs:
            matches = find_matches(inp, list(self.boundary_inputs.keys()))
            if len(matches) == 0:
                raise Exception(f'Pattern {inp} not found in model')
            for match in matches:
                self.submodel_inputs[match] = {'iface_name': match.replace('.', ':')}
            self.submodel_inputs.pop(inp)

        for out in wildcard_outputs:
            matches = find_matches(out, list(self.all_outputs.keys()))
            if len(matches) == 0:
                raise Exception(f'Pattern {out} not found in model')
            for match in matches:
                self.submodel_outputs[match] = {'iface_name': match.replace('.', ':')}
            self.submodel_outputs.pop(out)

        # NOTE iface_name is what the outer problem knows the variable to be
        # it can't be the same name as the prom name in the inner variable because
        # component var names can't include '.'
        for var in self.submodel_inputs.items():
            iface_name = var[1]['iface_name']
            if iface_name in self._static_var_rel2meta or iface_name in self._var_rel2meta:
                continue
            prom_name = var[0]
            try:
                meta = self.boundary_inputs[p.model.get_source(prom_name)] \
                    if not p.model.get_source(prom_name).startswith('_auto_ivc.') \
                    else self.boundary_inputs[prom_name]
            except Exception:
                raise Exception(f'Variable {prom_name} not found in model')
            meta.pop('prom_name')

            for key, val in var[1].items():
                if key == 'iface_name':
                    continue
                meta[key] = val

            super().add_input(iface_name, **meta)
            meta['prom_name'] = prom_name

        for var in self.submodel_outputs.items():
            iface_name = var[1]['iface_name']
            if iface_name in self._static_var_rel2meta or iface_name in self._var_rel2meta:
                continue
            prom_name = var[0]
            try:
                meta = self.all_outputs[prom_name]
            except Exception:
                raise Exception(f'Variable {prom_name} not found in model')
            meta.pop('prom_name')

            for key, val in var[1].items():
                if key == 'iface_name':
                    continue
                meta[key] = val

            super().add_output(iface_name, **meta)
            meta['prom_name'] = prom_name

    def _setup_var_data(self):
        super()._setup_var_data()

        p = self._subprob
        inputs = self._var_rel_names['input']
        outputs = self._var_rel_names['output']

        if len(inputs) == 0 or len(outputs) == 0:
            return

        for prom_name in self.submodel_inputs.keys():
            if prom_name in p.model._static_design_vars or prom_name in p.model._design_vars:
                continue
            p.model.add_design_var(prom_name)

        for prom_name in self.submodel_outputs.keys():
            # got abs name back for self._cons key for some reason in `test_multiple_setups`
            # TODO look into this
            if prom_name in p.model._responses:
                continue
            p.model.add_constraint(prom_name)

        # setup again to compute coloring
        p.set_solver_print(-1)
        if self._problem_meta is None:
            p.setup(force_alloc_complex=False)
        else:
            p.setup(force_alloc_complex=self._problem_meta['force_alloc_complex'])
        p.final_setup()

        self.coloring = p.driver._get_coloring(run_model=True)
        if self.coloring is not None:
            self.coloring._col_vars = list(p.driver._designvars)

        # self._reset_driver_vars()

        if self.coloring is None:
            self.declare_partials(of='*', wrt='*')
        else:
            for of, wrt, nzrows, nzcols, _, _, _, _ in self.coloring._subjac_sparsity_iter():
                self.declare_partials(of=of, wrt=wrt, rows=nzrows, cols=nzcols)

    def _set_complex_step_mode(self, active):
        super()._set_complex_step_mode(active)
        self._subprob.set_complex_step_mode(active)

    def compute(self, inputs, outputs):
        """
        Perform the subproblem system computation at run time.

        Parameters
        ----------
        inputs : Vector
            Unscaled, dimensional input variables read via inputs[key].
        outputs : Vector
            Unscaled, dimensional output variables read via outputs[key].
        """
        p = self._subprob

        for prom_name, meta in self.submodel_inputs.items():
            p.set_val(prom_name, inputs[meta['iface_name']])

        # set initial output vals
        for prom_name, meta in self.submodel_outputs.items():
            p.set_val(prom_name, outputs[meta['iface_name']])

        p.driver.run()

        for prom_name, meta in self.submodel_outputs.items():
            outputs[meta['iface_name']] = p.get_val(prom_name)

    def compute_partials(self, inputs, partials):
        """
        Collect computed partial derivatives and return them.

        Checks if the needed derivatives are cached already based on the
        inputs vector. Refreshes the cache by re-computing the current point
        if necessary.

        Parameters
        ----------
        inputs : Vector
            Unscaled, dimensional input variables read via inputs[key].
        partials : Jacobian
            Sub-jac components written to partials[output_name, input_name].
        """
        p = self._subprob

        for prom_name, meta in self.submodel_inputs.items():
            p.set_val(prom_name, inputs[meta['iface_name']])

        wrt = list(self.submodel_inputs.keys())
        of = list(self.submodel_outputs.keys())

        tots = p.driver._compute_totals(wrt=wrt,
                                        of=of,
                                        use_abs_names=False, driver_scaling=False)

        if self.coloring is None:
            for (tot_output, tot_input), tot in tots.items():
                input_iface_name = self.submodel_inputs[tot_input]['iface_name']
                output_iface_name = self.submodel_outputs[tot_output]['iface_name']
                partials[output_iface_name, input_iface_name] = tot
        else:
            for of, wrt, nzrows, nzcols, _, _, _, _ in self.coloring._subjac_sparsity_iter():
                partials[of, wrt] = tots[of, wrt][nzrows, nzcols].ravel()

```

## Example

```python
from numpy import pi
import openmdao.api as om


 p = om.Problem()

model = om.Group()
model.add_subsystem('supComp', om.ExecComp('z = x**2 + y'),
                    promotes_inputs=['x', 'y'],
                    promotes_outputs=['z'])

submodel1 = om.Group()
submodel1.add_subsystem('sub1_ivc_r', om.IndepVarComp('r', 1.),
                        promotes_outputs=['r'])
submodel1.add_subsystem('sub1_ivc_theta', om.IndepVarComp('theta', pi),
                        promotes_outputs=['theta'])
submodel1.add_subsystem('subComp1', om.ExecComp('x = r*cos(theta)'),
                        promotes_inputs=['r', 'theta'],
                        promotes_outputs=['x'])

submodel2 = om.Group()
submodel2.add_subsystem('sub2_ivc_r', om.IndepVarComp('r', 2),
                        promotes_outputs=['r'])
submodel2.add_subsystem('sub2_ivc_theta', om.IndepVarComp('theta', pi/2),
                        promotes_outputs=['theta'])
submodel2.add_subsystem('subComp2', om.ExecComp('y = r*sin(theta)'),
                        promotes_inputs=['r', 'theta'],
                        promotes_outputs=['y'])

subprob1 = om.Problem()
subprob1.model.add_subsystem('submodel1', submodel1)
subprob1.model.promotes('submodel1', any=['*'])

subprob2 = om.Problem()
subprob2.model.add_subsystem('submodel2', submodel2)
subprob2.model.promotes('submodel2', any=['*'])

subcomp1 = om.SubmodelComp(problem=subprob1,
                           inputs=['r', 'theta'], outputs=['x'])
subcomp2 = om.SubmodelComp(problem=subprob2,
                           inputs=['r', 'theta'], outputs=['y'])

p.model.add_subsystem('sub1', subcomp1, promotes_inputs=['r','theta'],
                            promotes_outputs=['x'])
p.model.add_subsystem('sub2', subcomp2, promotes_inputs=['r','theta'],
                            promotes_outputs=['y'])
p.model.add_subsystem('supModel', model, promotes_inputs=['x','y'],
                            promotes_outputs=['z'])

p.model.set_input_defaults('r', 1)
p.model.set_input_defaults('theta', pi)

p.setup(force_alloc_complex=True)

p.run_model()
cpd = p.check_partials(method='cs', out_stream=None)
print(f"x = {p.get_val('x')}")
print(f"y = {p.get_val('y')}") 
print(f"z = {p.get_val('z')}")

# om.n2(prob)
```

## Outputs

```
--------------------------------
Component: SubmodelComp 'sub1'
--------------------------------

  sub1: 'x' wrt 'r'
    Analytic Magnitude: 1.000000e+00
          Fd Magnitude: 1.000000e+00 (cs:None)
    Absolute Error (Jan - Jfd) : 0.000000e+00

    Relative Error (Jan - Jfd) / Jfd : 0.000000e+00

    Raw Analytic Derivative (Jfor)
[[-1.]]

    Raw CS Derivative (Jcs)
[[-1.]]
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  sub1: 'x' wrt 'theta'
    Analytic Magnitude: 1.224647e-16
          Fd Magnitude: 1.224647e-16 (cs:None)
    Absolute Error (Jan - Jfd) : 0.000000e+00

    Relative Error (Jan - Jfd) / Jfd : 0.000000e+00

    Raw Analytic Derivative (Jfor)
[[-1.2246468e-16]]

    Raw CS Derivative (Jcs)
[[-1.2246468e-16]]
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
--------------------------------
Component: SubmodelComp 'sub2'
--------------------------------

  sub2: 'y' wrt 'r'
    Analytic Magnitude: 1.224647e-16
          Fd Magnitude: 1.224647e-16 (cs:None)
    Absolute Error (Jan - Jfd) : 0.000000e+00

    Relative Error (Jan - Jfd) / Jfd : 0.000000e+00

    Raw Analytic Derivative (Jfor)
[[1.2246468e-16]]

    Raw CS Derivative (Jcs)
[[1.2246468e-16]]
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  sub2: 'y' wrt 'theta'
    Analytic Magnitude: 1.000000e+00
          Fd Magnitude: 1.000000e+00 (cs:None)
    Absolute Error (Jan - Jfd) : 0.000000e+00

    Relative Error (Jan - Jfd) / Jfd : 0.000000e+00

    Raw Analytic Derivative (Jfor)
[[-1.]]

    Raw CS Derivative (Jcs)
[[-1.]]
 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
x = [-1.]
y = [1.2246468e-16]
z = [1.]
```
