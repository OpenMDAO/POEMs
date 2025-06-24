POEM ID: 104  
Title:  Add PETSc Linear Solvers  
authors: robfalck (Rob Falck), rob-hetterich (Rob Hetterich)  
Competing POEMs: None  
Related POEMs:  None  
Associated implementation PR: [#3549](https://github.com/OpenMDAO/OpenMDAO/pull/3549)  

Status:  

- [ ] Active  
- [x] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation

The default implementation of DirectSolver, which uses Scipy's implementation of SuperLU is sometimes slower than other direct linear solvers available, notably umfpack and klu.


## Description

These linear solvers are available in PETSc, which is already an optional dependency of OpenMDAO. These solvers will be available via the new `PETScDirectSolver` class.

The linear solver solves the system `Ax = b`, and in OpenMDAO this is generally used to solve for total derivatives using the unified derivatives equations.

The user may specify a linear solver algorithm to use internally via the `sparse_solver_name` option.  This may be one of the following serial algorithms:

- `'superlu'`
- `'klu'`
- `'umfpack'`
- `'petsc'`

or the following distributed algorithms:
- `'mumps'`
- `'superlu_dist'`

The latter two solvers are available under MPI, while the first four may only be used in serial mode.




