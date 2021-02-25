POEM ID:  042  
Title:  DOEDriver different number of levels for different DVs.  
authors: @onodip (Péter Onódi)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: [#1885](https://github.com/OpenMDAO/OpenMDAO/pull/1885)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation
In the current DOEDriver in a Full Factorial design all design variables must have the same number of levels.
This might be inconvenient, when a different resolution is needed for different variables. In pyDOE2 both 
Full Factorial and General Subset Design (GSD) support the individual assignment for each factor. 

## Description
An example to specify levels individually:

    import numpy as np
    import openmdao.api as om
    from openmdao.test_suite.components.paraboloid import Paraboloid
    
    prob = om.Problem()
    model = prob.model
    
    model.add_subsystem('comp', Paraboloid(), promotes=['x', 'y', 'f_xy'])
    model.set_input_defaults('x', 0.0)
    model.set_input_defaults('y', 0.0)
    model.add_design_var('x', lower=0.0, upper=10.0)
    model.add_design_var('y', lower=0.0, upper=5.0)
    model.add_objective('f_xy')
    
    prob.driver = om.DOEDriver(generator=om.FullFactorialGenerator(levels={"x": 3, "y": 2}))
    prob.driver.add_recorder(om.SqliteRecorder("cases.sql"))
    
    prob.setup()
    prob.run_driver()
    prob.cleanup()
    
    cr = om.CaseReader("cases.sql")
    cases = cr.list_cases('driver', out_stream=None)
    
    for case in cases:
        outputs = cr.get_case(case).outputs
        print('    '.join([f"{name}: {float(outputs[name])}" for name in ('x', 'y', 'f_xy')]))

Results in 2 x 3 = 6 designs:

    x: 0.0    y: 0.0    f_xy: 22.0
    x: 5.0    y: 0.0    f_xy: 17.0
    x: 10.0    y: 0.0    f_xy: 62.0
    x: 0.0    y: 5.0    f_xy: 87.0
    x: 5.0    y: 5.0    f_xy: 107.0
    x: 10.0    y: 5.0    f_xy: 177.0

PR #1885 also implements the GSD generator from pyDOE2. The same definition of levels can be
used for GSD as for Full factorial.

