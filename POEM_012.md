POEM ID: 012 
Title: Give the user the option to select the LAPACK driver for use in the SVD used in KrigingSurrogate  
authors: [hschilling] ([Herb Schilling])   
Competing POEMs: None
Related POEMs: None
Associated implementation PR: 1185

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------
The `MetaModelTestCase.test_sin_metamodel_preset_data` in `components/tests/test_meta_model_unstructured_compy.py` test was failing with recent versions of scipy.

For example, for these versions of `numpy` and `scipy`:

```
numpy==1.18.1
scipy==1.4.1
```

the `MetaModelTestCase.test_sin_metamodel_preset_data` fails with

```
Traceback (most recent call last):
File "/Users/hschilli/anaconda/envs/py37/lib/python3.7/site-packages/testflo/test.py", line 473, in _try_call
func()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/components/tests/test_meta_model_unstructured_comp.py", line 126, in test_sin_metamodel_preset_data
prob.run_model()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/core/problem.py", line 554, in run_model
self.model.run_solve_nonlinear()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/core/system.py", line 3605, in run_solve_nonlinear
self._solve_nonlinear()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/core/group.py", line 1644, in _solve_nonlinear
self._nonlinear_solver.solve()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/solvers/nonlinear/nonlinear_runonce.py", line 40, in solve
self._gs_iter()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/solvers/solver.py", line 677, in _gs_iter
subsys._solve_nonlinear()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/core/explicitcomponent.py", line 271, in _solve_nonlinear
self.compute(self._inputs, self._outputs)
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/components/meta_model_unstructured_comp.py", line 348, in compute
self._train()
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/components/meta_model_unstructured_comp.py", line 610, in _train
self._training_output[name])
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/surrogate_models/kriging.py", line 138, in train
bounds=bounds)
File "/Users/hschilli/anaconda/envs/py37/lib/python3.7/site-packages/scipy/optimize/_minimize.py", line 608, in minimize
constraints, callback=callback, *options)
File "/Users/hschilli/anaconda/envs/py37/lib/python3.7/site-packages/scipy/optimize/slsqp.py", line 399, in _minimize_slsqp
fx = func(x)
File "/Users/hschilli/anaconda/envs/py37/lib/python3.7/site-packages/scipy/optimize/optimize.py", line 326, in function_wrapper
return function((wrapper_args + args))
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/surrogate_models/kriging.py", line 131, in _calcll
loglike = self._calculate_reduced_likelihood_params(np.exp(thetas))[0]
File "/Users/hschilli/Documents/OpenMDAO/dev/OpenMDAO/openmdao/surrogate_models/kriging.py", line 184, in _calculate_reduced_likelihood_params
[U, S, Vh] = linalg.svd(R)
File "/Users/hschilli/anaconda/envs/py37/lib/python3.7/site-packages/scipy/linalg/decomp_svd.py", line 132, in svd
raise LinAlgError("SVD did not converge")
numpy.linalg.LinAlgError: SVD did not converge
```

The `KrigingSurrogate` makes use of scipy's `linalg.svd` function in its `_calculate_reduced_likelihood_params` method`. 
The function `linalg.svd` has an option to set the LAPACK driver that it uses. `KrigingSurrogate` uses the default LAPACK driver, `'gesdd'`. The other option is `'gesvd'`.

Onlne research showed that `'gesdd'` is faster but not as robust. The other driver,`'gesvd'`, is slower but more reliable.

It was decided that while speed is important, robustness is more important so the
default behavior will be reliable rather than fast, but the user is given an option to use either LAPACK driver, `'gesdd'` or `'gesvd'`.


Description
-----------
An API change will be made to the `KrigingSurrogate` constructor. An optional parameter, `lapack_driver` will be added. The 
default will be `'gesvd'`. The user can choose to use the other LAPACK driver by setting the parameter to `'gesvd'`.

For example,

```
om.KrigingSurrogate(lapack_driver='gesdd')
```






