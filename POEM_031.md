POEM ID: 031   
Title: Improved Aitken Relaxation  
authors: [justinsgray]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR: #1590

Status:

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  



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

Add the new option `aitken_initial_factor` with a default value of 0.4. 
Since 0.4 is a backwards incompatible change with the default of 1.0 in OpenMDAO V3.2.1, 
We can first add the new option to the nonlinear solver but leave the default at 1.0. 
When Aitken is active, we can throw a deprecation warning stating that the default will change from 1.0 to 0.4 in the next version. 
Then then in the next version, we can change the default and add the Aitken algorithm to the linear solver as well. 

I am proposing the intermediate release only include the new option on the nonlinear solver specifically to limit the amount of backwards incompatible changes we create (even if they are only for a single transition release). 






