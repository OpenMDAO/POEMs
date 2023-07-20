POEM ID: 089   
Title: Optimization efficiency improvements (relevance reduction revisited).  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [2942](https://github.com/OpenMDAO/OpenMDAO/pull/2942)

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [ ] Rejected
- [x] Integrated

## Motivation

Users often build models where a few relatively expensive
"pre-compute" components may need to be evaluated to determine 
inputs for subsequent components during optimization, but these components do not need to
be evaluated again during the optimization process.

Similarly, components that exist primarily to provide "auxiliary" outputs that are informational
but not necessary for the optimization itself do not need to be run during each driver iteration.

The OpenMDAO development team intends to address this situation to make optimization more efficient.

## Proposed Solution

OpenMDAO Problem objects will get a new option, `"group_by_pre_opt_post"`.

If set to True, subsystems in the top level of the model will be sorted into those which are needed pre-optimization,
those which need to be evaluated during the optimization, and those whose evaluation can be delayed until
the optimization has been completed.

Under the hood, OpenMDAO will use a graph of the problem to determine which systems belong
in the pre/opt/post sets.

Initially this capability will be documented as an experimental feature and will be disabled by default.

Users using this feature may notice different behavior in things like recording, since some systems are no
longer being evaluated during each driver iteration.

Any group having a nonlinear solver that computes gradients will be treated as atomic with respect to
placement in pre/opt/post, meaning that if any component under that group is in opt, then all of that
group's components (direct or indirect) will be in opt.
In fact, if a given group has a NL solver using gradients then the only way its components will end up
in pre or post is if all of them are in pre or all in post.
If some are in pre and some in post then all will have to be placed in opt.
For other groups not having a NL solver using gradients, their components can be split up among pre, opt, and/or post.
