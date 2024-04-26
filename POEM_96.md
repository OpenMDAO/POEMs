POEM ID:  096
Title:  Research and Pseudocode of Manual Reverse Mode differentiation
authors: jsrogan, coleyoung5
Competing POEMs:  N/A
Related POEMs: N/A
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated



## Motivation
Considering the fact that private optimization libraries such as SNOPT offer the ability to find a feasible starting point, it makes sense that OPENMdao should also have that functionality. Aditionally OPENMdao's current components do not calculate reverse derivatives, so the implementation of this is also necessary (and still ongoing).



## Description
In order to implement this we researched helpful libraries to implement a tree like structure which would allow us to perform reverse mode differentation while backtracking, and wrote pseudocode which explains our choices and our insights into the problem. While not a full solution by any means, hopefully this provides a strong starting point for others who are looking to implement this problem.



