POEM ID: 031   
Title: Improved Aitken Relaxation  
authors: [justinsgray]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR: #1590, #1663 

Status:

- [ ] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [x] Integrated  



Motivation
----------
Aitken relaxation/acceleration improves both the stability and the convergence speed when using GaussSeidel solvers to converge implicit systems. 
The implementation in OpenMDAO 3.2.1 is only applied to the nonlinear solver, but could be extended to the linear solver as well. 
In addition, the current implementation hard-codes the initial relaxation factor to 1.0. 
The recommended starting value is 0.4, so we don't follow best practices there and we hard-code the value. 

To provide a consistent interface for the nonlinear and linear block gauss-sidel solvers, we can add a user facing option to control the starting relaxation factor and implement the algorithm for both the linear and nonlinear solvers. 

Description
-----------

Implement the aitken relaxation/acceleration algorithm in the the linear block GaussSeidel algorithm, and add a consistent set of control options in both solvers. 

Keep the default initial factor as 1.0






