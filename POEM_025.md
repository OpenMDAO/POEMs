POEM ID: 025  
Title: allow GA to seek pareto frontier  
authors: [Kenneth-T-Moore]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:  [#1459](https://github.com/OpenMDAO/OpenMDAO/pull/1459)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

As a substep in the AMIEGO multiple infill point strategy we needed to find a set of non-dominated candidates.

Description
-----------

Adds a new option "compute_pareto" to `SimpleGADriver` defaulting to False. When it is set to True in the
multi-objective case, instead of computing a weighted some of the objectives, determine a set of non-dominated
points from the population of genes and keep track of this set rather than just the best point. A new
tournament selection method suitable for multiple objective values will also be added.


