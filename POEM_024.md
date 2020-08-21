POEM ID: 024   
Title: Calculating ExecComp Jacobian with symbolic derivatives  
authors: [onodip] (Péter Onódi)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


Motivation
----------

Although accurate approximate derivatives can be calculated with the complex step method, the restricted syntax 
of the ExecComp could allow to calculate exact derivatives without the need of a complete automatic 
differentiation framework. Except the overhead at setup it should be comparably fast as writing analytic derivatives.

Description
-----------

For the prototype implementation the `sympy` package was used. It might be an overkill to add `sympy` as a 
dependency. Most likely with an expression interpreter and implementing some common derivative calculation 
rules would also work fine. I think this functionality could be either part of ExecComp with a user option, 
or maybe a separate component. If it will need the extra dependency, it might be better to implement it  as a plugin.

A simplified implementation is included below, which is restricted to scalar variables.
With this code the Sellar problem was optimized around 30% faster (without any code optimization) compared to 
the same problem with `ExecComp`s and complex step.

```
from collections import OrderedDict

from sympy import symbols, diff
from sympy.core.sympify import sympify

import openmdao.api as om


class SymbExecComp(om.ExecComp):
    """Like an ExecComp, but it can calculate partials with symbolic derivatives."""

    def __init__(self, *args, **kwargs):
        options = {}
        for name in ('partial_method',):
            if name in kwargs:
                options[name] = kwargs.pop(name)
        super(SymbExecComp, self).__init__(*args, **kwargs)
        self.options.update(options)
        self._input_symbols = None
        self._output_symbols = None
        self._partial_symbols = OrderedDict()
        self._exprs_symbols = []

    def initialize(self):
        super(SymbExecComp, self).initialize()
        self.options.declare('partial_method', default='exact', values=('cs', 'exact'),
                             desc="The type of approximation that should be used. Valid options include: "
                                  "'cs': Complex Step, 'exact': use symbolic derivatives. "
                                  "Default is 'exact'.")

    def setup(self):
        super(SymbExecComp, self).setup()
        input_names = self._var_rel_names['input']
        output_names = self._var_rel_names['output']

        if self.options['partial_method'] == 'exact':
            self._input_symbols = OrderedDict([(name, symbols(name)) for name in input_names])
            self._output_symbols = OrderedDict([(name, symbols(name)) for name in output_names])
            self._exprs_symbols = [sympify(expr.split("=")[-1]) for expr in self._exprs]  # Get left hand side
            for expr, out in zip(self._exprs_symbols, output_names):
                self._partial_symbols[out] = OrderedDict()
                for inp, inp_symb in zip(input_names, self._input_symbols):
                    self._partial_symbols[out][inp] = diff(expr, inp_symb)
            self.declare_partials('*', '*', method='exact')

    def compute_partials(self, inputs, partials):
        if self.options['partial_method'] == 'cs':
            super(SymbExecComp, self).compute_partials(inputs, partials)
        else:  # Symbolic derivatives
            output_names = self._var_rel_names['output']
            names_and_vals = [(inp, float(inputs[inp])) for inp in inputs]  # Works only with scalar for now
            for out in output_names:
                for inp in inputs:
                    val = self._partial_symbols[out][inp].subs(names_and_vals)
                    partials[out, inp] = val


class Sellar(om.Group):
    """
    Sellar problem.
    """

    def setup(self):
        indeps = self.add_subsystem('indeps', om.IndepVarComp(), promotes=['*'])
        indeps.add_output('x', 1.0)
        indeps.add_output('z1', 5.0)
        indeps.add_output('z2', 2.0)
        cycle = self.add_subsystem('cycle', om.Group(), promotes=['*'])
        cycle.add_subsystem('d1', SymbExecComp("y1 = z1**2 + z2 + x - 0.2*y2"),
                            promotes_inputs=['x', 'z1', 'z2', 'y2'], promotes_outputs=['y1'])
        cycle.add_subsystem('d2', SymbExecComp("y2 = y1**0.5 + z1 + z2"),
                            promotes_inputs=['z1', 'z2', 'y1'], promotes_outputs=['y2'])

        cycle.nonlinear_solver = om.NonlinearBlockGS()

        self.add_subsystem('obj_cmp', SymbExecComp('obj = x**2 + z2 + y1 + exp(-y2)', z2=0.0, x=0.0),
                           promotes=['x', 'z2', 'y1', 'y2', 'obj'])

        self.add_subsystem('con_cmp1', SymbExecComp('con1 = 3.16 - y1'),
                           promotes=['con1', 'y1'])
        self.add_subsystem('con_cmp2', SymbExecComp('con2 = y2 - 24.0'),
                           promotes=['con2', 'y2'])


if __name__ == '__main__':
    p = om.Problem(model=Sellar())
    model = p.model
    p.driver = om.ScipyOptimizeDriver()

    model.add_design_var('z1', lower=-10.0, upper=10.0)
    model.add_design_var('z2', lower=0.0, upper=10.0)
    model.add_design_var('x', lower=0.0, upper=10.0)
    model.add_objective('obj')
    model.add_constraint('con1', equals=0.0)
    model.add_constraint('con2', upper=0.0)

    p.setup(force_alloc_complex=True)
    p.run_driver()
    print("z1 = ", p['z1'])
    print("z2 = ", p['z2'])
    print("x = ", p['x'])
    print("obj = ", p['obj'])

```


Rejection Justification
-----------------------

Performance benchmarking done by @onodip found that in nearly every use case (certainly all common use cases) the performance of CS equal to or better than that of SymPy. 
Given the limited potential gains, the additional dependency and code complexity for this POEM was deemed too much to justify adoption by the dev team. 
