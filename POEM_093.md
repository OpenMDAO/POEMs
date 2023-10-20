POEM ID: 093  
Title: Linear solution caching  
authors: kanekosh (Shugo Kaneko) and anilyil (Anil Yildirim)  
Competing POEMs:   
Related POEMs:  
Associated implementation PR:  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation
When computing derivatives with a hierarchical linear solver, OpenMDAO may re-solve the same subsystem-level linear system multiple times, which is redundant.
Examples of such problems will be provided later.  
This POEM proposes to remove this redundancy and accelerate the total derivatives computation by caching the subsystem-level linear solutions.

## Description
We suggest caching the right-hand side (RHS) vector `b` and the corresponding linear system solution `x` within the subsystem's linear solver.
The caching can be optional; by default, it would not cache the solution to  avoid unnecessary overhead of saving/checking the cache.  
When the user enabled caching, the linear solver checks if the given RHS vector `b` is parallel to a cached vector `b_cache` before solving the linear system.
If they are parallel, it returns the linear system solution by `x = x_cache * (|b| / |b_cache|)` without solving the linear system.
Otherwise, it solves the linear solver and add the solution and corresponding RHS vector to the cache.

## API change proposal

**1. Caching all inputs or outputs of a subsystem**  
A user may enable the caching when adding a linear solver to a subsystem.  
For example,

```python
subsystem1.linear_solver = om.PETScKrylov(use_cache=True)
```
would enable caching for `subsystem1`.
This does not change the behavior of the current models if we set the default to `use_cache=False`.

**2. Caching specific inputs or outputs**   
Furthermore, enabling the caching only for the user-specified inputs (in forward mode) or outputs (in reverse mode) can further reduce the computational overhead of the caching.  
For example,
```python
subsystem.use_cache(mode='rev', cache_inputs=None, cache_outputs=['Lift'])
```
would enable caching only for the `Lift` output in the reverse mode, but not for other outputs.

## Prototype implementation
We implemented a prototype of the linear solution caching in a custom PETScKrylov solver and Direct solver, which are available [here](POEM_093/).

Note that this prototype caches all the inputs or outputs of a subsystem (i.e., it implements the proposal 1 above).
The implementation of the caching for specific inputs or outputs (proposal 2) would require a different approach (which we don't have a good idea of how it can be done).  
Also note that this prototype does not implement the cache resetting, which should be done every optimization iterations.

Here, we explain how the caching would be implemented for a Krylov solver.
It works mostly the same for a Direct solver.
The complete custom solver file is available [here](POEM_093/petsc_ksp_custom.py).

First, we add a new option for caching:
```python
def _declare_options(self):
    """
    Declare options before kwargs are processed in the init method.
    """
    super()._declare_options()

    self.options.declare('ksp_type', default='fgmres', values=KSP_TYPES,
                            desc="KSP algorithm to use. Default is 'fgmres'.")

    self.options.declare('restart', default=1000, types=int,
                            desc='Number of iterations between restarts. Larger values increase '
                            'iteration cost, but may be necessary for convergence')

    self.options.declare('precon_side', default='right', values=['left', 'right'],
                            desc='Preconditioner side, default is right.')

    # --- option for caching. Default: no cache ---
    self.options.declare('use_cache', types=bool, default=False)

    # changing the default maxiter from the base class
    self.options['maxiter'] = 100
```

Then, the solver initializes the cache in `_linearize` (or in `__init__`):
```python
def _linearize(self):
    """
    Perform any required linearization operations such as matrix factorization.
    """
    print('*** linearize in Krylov ***')
    if self.precon is not None:
        self.precon._linearize()

    # --- initialize cache ---
    if self.options['use_cache']:
        self._rhs_cache_list = []
        self._sol_cache_list = []
```

In the `solve` method, it checks and reuses the cached solution if applicable.
Otherwise, it adds the RHS vector and the solution to the cache at the end.
```python
def solve(self, mode, rel_systems=None):
    """
    Solve the linear system for the problem in self._system().

    The full solution vector is returned.

    Parameters
    ----------
    mode : str
        Derivative mode, can be 'fwd' or 'rev'.
    rel_systems : set of str
        Names of systems relevant to the current solve.
    """
    self._rel_systems = rel_systems
    self._mode = mode

    system = self._system()
    options = self.options

    if system.under_complex_step:
        raise RuntimeError('{}: PETScKrylov solver is not supported under '
                            'complex step.'.format(self.msginfo))

    maxiter = options['maxiter']
    atol = options['atol']
    rtol = options['rtol']

    # assign x and b vectors based on mode
    if self._mode == 'fwd':
        x_vec = system._doutputs
        b_vec = system._dresiduals
    else:  # rev
        x_vec = system._dresiduals
        b_vec = system._doutputs

    # create numpy arrays to interface with PETSc
    sol_array = x_vec.asarray(copy=True)
    rhs_array = b_vec.asarray(copy=True)

    # --- check if we can reuse the cached solutions ---
    if self.options['use_cache']:
        for i, rhs_cache in enumerate(self._rhs_cache_list):   # loop over cached RHS vectors. NOTE: reverse order loop would be faster?
            # Check if the RHS vector is the same as a cached vector. This part is not necessary, but is less expensive than checking if two vectors are parallel.
            if np.allclose(rhs_array, rhs_cache, rtol=1e-12, atol=1e-12):
                x_vec.set_val(self._sol_cache_list[i])
                print('*** use caching in Krylov with scaler = 1', 'time =', time.time() - time0, '***')
                return
            # Check if the RHS vector is equal to -1 * cached vector.
            elif np.allclose(rhs_array, -rhs_cache, rtol=1e-12, atol=1e-12):
                x_vec.set_val(-self._sol_cache_list[i])
                print('*** use caching in Krylov with scaler = -1', 'time =', time.time() - time0, '***')
                return
            
            # Check if the RHS vector and a cached vector are parallel
            # NOTE: the following parallel vector check may be inaccurate for some cases. maybe should tighten the tolerance?
            dot_product = np.dot(rhs_array, rhs_cache)
            norm1 = np.linalg.norm(rhs_array)
            norm2 = np.linalg.norm(rhs_cache)
            if np.isclose(abs(dot_product), norm1 * norm2, rtol=1e-12, atol=1e-12):
                # two vectors are parallel, thus we can use the cache.
                scaler = dot_product / norm2**2
                x_vec.set_val(self._sol_cache_list[i] * scaler)
                print('*** use caching in Krylov with scaler =', scaler, ' | time =', time.time() - time0, '***')
                return
    
    # create PETSc vectors from numpy arrays
    sol_petsc_vec = PETSc.Vec().createWithArray(sol_array, comm=system.comm)
    rhs_petsc_vec = PETSc.Vec().createWithArray(rhs_array, comm=system.comm)

    # run PETSc solver
    self._iter_count = 0
    ksp = self._get_ksp_solver(system)
    ksp.setTolerances(max_it=maxiter, atol=atol, rtol=rtol)
    ksp.solve(rhs_petsc_vec, sol_petsc_vec)

    # stuff the result into the x vector
    x_vec.set_val(sol_array)

    sol_petsc_vec = rhs_petsc_vec = None

    # --- append the current solution to the cache ---
    if self.options['use_cache']:
        self._rhs_cache_list.append(rhs_array.copy())
        self._sol_cache_list.append(sol_array.copy())
```

## Examples of Caching: 
### 2-point Aerostructural optimization
Here is an [OpenAeroStruct multipoint optimization example](POEM_093/example1.py) to demonstrate the solution caching.
We consider the following optimization problem:
```
minimize:   CD0 + CD1
subject to: CL0 = 0.6
            CL1 - CL0 = 0.2
```

For the second operating point, we impose the CL constraint in a way that it also depends on the first point's CL.
To compute the total derivatives, we use PETScKrylov solver for aerostructural coupling.
The solver outputs of `compute_totals()` look as follows:
```
# dCD0/dx
LN: PETScKrylov 0 ; 0.00299022306 1
LN: PETScKrylov 1 ; 8.49989958e-08 2.84256372e-05
LN: PETScKrylov 2 ; 7.30820654e-11 2.44403391e-08

# dCD1/dx
LN: PETScKrylov 0 ; 0.00333369362 1
LN: PETScKrylov 1 ; 8.50541382e-08 2.55134838e-05
LN: PETScKrylov 2 ; 8.31048387e-11 2.49287572e-08

# dCL0/dx
LN: PETScKrylov 0 ; 0.00951495633 1
LN: PETScKrylov 1 ; 2.65013995e-06 0.000278523607
LN: PETScKrylov 2 ; 1.22310119e-09 1.28545118e-07
LN: PETScKrylov 3 ; 1.82688692e-11 1.92001608e-09

# dCL1/dx
LN: PETScKrylov 0 ; 0.00952340656 1
LN: PETScKrylov 1 ; 2.64776928e-06 0.000278027538
LN: PETScKrylov 2 ; 1.04735578e-09 1.0997701e-07
LN: PETScKrylov 3 ; 1.19985619e-11 1.25990231e-09

# dCL0/dx again - identical history to the previous dCL0/dx solve.
LN: PETScKrylov 0 ; 0.00951495633 1
LN: PETScKrylov 1 ; 2.65013995e-06 0.000278523607
LN: PETScKrylov 2 ; 1.22310119e-09 1.28545118e-07
LN: PETScKrylov 3 ; 1.82688692e-11 1.92001608e-09

# verification print
Derivatives of CL_diff w.r.t. twist_cp = [[-2.17863550e-05 -3.79972743e-05 -4.59107509e-05 -4.77229851e-05]]
```
We can observe that there were 5 aerostructural adjoint solves: 2 for objective, 1 for the first CL constraint, and 2 for the second CL constraint.
However, there are duplicated adjoint solve for `dCL0/dx` because `CL0` is used for both the first and second CL constraints.

This duplicated adjoint solves can be avoided using the solution caching.
Using [the prototype solver](POEM_093/petsc_ksp_custom.py), we get the following solver outputs:
```
# dCD0/dx
LN: PETScKrylov 0 ; 0.00299022306 1
LN: PETScKrylov 1 ; 8.49989958e-08 2.84256372e-05
LN: PETScKrylov 2 ; 7.30820654e-11 2.44403391e-08
*** solved in Krylov | time = 8.14E-03 s ***

# dCD1/dx
LN: PETScKrylov 0 ; 0.00333369362 1
LN: PETScKrylov 1 ; 8.50541382e-08 2.55134838e-05
LN: PETScKrylov 2 ; 8.31048387e-11 2.49287572e-08
*** solved in Krylov | time = 7.97E-03 s ***

# dCL0/dx
LN: PETScKrylov 0 ; 0.00951495633 1
LN: PETScKrylov 1 ; 2.65013995e-06 0.000278523607
LN: PETScKrylov 2 ; 1.22310119e-09 1.28545118e-07
LN: PETScKrylov 3 ; 1.82688692e-11 1.92001608e-09
*** solved in Krylov | time = 1.00E-02 s ***

# dCL1/dx
LN: PETScKrylov 0 ; 0.00952340656 1
LN: PETScKrylov 1 ; 2.64776928e-06 0.000278027538
LN: PETScKrylov 2 ; 1.04735578e-09 1.0997701e-07
LN: PETScKrylov 3 ; 1.19985619e-11 1.25990231e-09
*** solved in Krylov | time = 1.01E-02 s ***

# dCL0/dx again - now use cached solution without running the Krylov solver
*** use caching in Krylov with scaler = -1 | time = 6.11E-04 s ***

# verification print
Derivatives of CL_diff w.r.t. twist_cp = [[-2.17863550e-05 -3.79972743e-05 -4.59107509e-05 -4.77229851e-05]]
```
The caching removed the redundant `dCL0/dx` solve but still gave the identical total derivatives (verified by printed CL_diff w.r.t. twist_cp).

### More practical multipoint problem
In the above example, we formulate the second CL constraint in a weird way to demonstrate the caching.
However, the above model structure represents practical problems.

As an example, we again consider [another multipoint problem](POEM_093/example2.py) (cruise point + manuever point), but now with more practical objective and constraints:  
```
minimize:   fuel burn  
subject to: L = W at cruise point
            L = W at maneuver point
```

The `L=W` constraints depend on the fuel burn, which is computed using the cruise drag.
Therefore, `L=W` constraint at the maneuver point depends on the fuel burn (or cruise drag) of the cruise point.
This introduces the redundant adjoint solves, i.e., the adjoint for maneuver point `L=W` calls the adjoint for cruise point.

The linear solution caching can avoid this redundancy.
The following is the linear solver outputs with caching:
```
# adjoint for fuelburn (cruise point OAS adjoint)
LN: PETScKrylov 0 ; 244.940409 1
LN: PETScKrylov 1 ; 0.00367094295 1.49870859e-05
LN: PETScKrylov 2 ; 5.5435276e-06 2.2632148e-08
LN: PETScKrylov 3 ; 2.08827096e-08 8.5256286e-11
*** solved in Krylov | time = 1.22E-02 s ***

# adjoint for L=W at cruise point
LN: PETScKrylov 0 ; 0.00787944105 1
LN: PETScKrylov 1 ; 4.18719356e-06 0.000531407436
LN: PETScKrylov 2 ; 2.89301257e-09 3.67159618e-07
LN: PETScKrylov 3 ; 1.68153368e-12 2.13407736e-10
*** solved in Krylov | time = 9.81E-03 s ***

# adjoint for L=W at maneuver point. This uses cache from the cruise point adjoint
LN: PETScKrylov 0 ; 1.70385305e-05 1
LN: PETScKrylov 1 ; 1.50491383e-06 0.0883241564
LN: PETScKrylov 2 ; 9.45843606e-10 5.55120411e-05
LN: PETScKrylov 3 ; 5.54498891e-13 3.25438213e-08
*** solved in Krylov | time = 1.17E-02 s ***
*** use caching in Krylov with scaler = 1.19E-05 | time = 4.44E-04 s ***
```

