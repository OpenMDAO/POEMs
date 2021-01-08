POEM ID: 033    
Title: Linear Constraints in Check Totals  
authors: [justinsgray]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR:   

Status:

- [ ] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [x] Integrated  



Motivation
----------
It is confusing to users when they don't see their constraints show up in `check_totals` output, and the value of their linear constraint gradients might be wrong. 
For both of these reasons, we need to include these in the output of `check_totals`

Description
-----------

It turns out that this was just a bug. With the bug fixed, check_totals includes the linear constraints.
```






