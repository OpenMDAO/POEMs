POEM ID: 033    
Title: Linear Constraints in Check Totals  
authors: [justinsgray]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR:   

Status:

- [ ] Active  
- [ ] Requesting decision  
- [x] Accepted  
- [ ] Rejected  
- [ ] Integrated  



Motivation
----------
It is confusing to users when they don't see their constraints show up in `check_totals` output, and the value of their linear constraint gradients might be wrong. 
For both of these reasons, we need to include these in the output of `check_totals`

Description
-----------

The simplest solution would be to simply add these constraints to the total derivative checking and include them in the output all the time. 
However, some problems may have a lot of linear constraints and it could be expensive to check them all. 

The proposed solution is to add a `linear_constraints` argument to the `check_totals` methods. 
It should default to `True`, even though this will be a mile backwards incompatibility. 
For any users who need to retain the old behavior, adding the argument to their call should be simple enough. 

The linear constraints should be clearly marked as such in the `check_totals` output like this: 

```
  Full Model: 'obj' wrt 'x' (linear constraint)
    Forward Magnitude : 2.980614e+00
         Fd Magnitude : 2.980617e+00 (fd:None)
    Absolute Error (Jfor  - Jfd) : 3.404818e-06 *

    Relative Error (Jfor  - Jfd) : 1.142320e-06 *

    Raw Forward Derivative (Jfor)
[[2.98061391]]

    Raw FD Derivative (Jfd)
[[2.98061732]]
```






