POEM ID: 023  
Title:  Remove reconfigure code from the current code base  
authors: [naylor-b] (Bret Naylor)    
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [x] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------

Early on in OpenMDAO's development, some support was added for dynamic reconfiguration of systems,
i.e. systems that changed during `_solve_nonlinear` by resizing variables, adding/removing variables, 
changing mpi communicators, etc., but the implementation of this support was very preliminary and 
was never tested on anything other than very simple toy problems.  It has since been determined that
to make this feature robust and usable with real world problems will require a complete redesign as
well as more specific requirements.  The existing code adds complexity to the setup stack and uses 
some system resources unnecessarily, given that this feature isn't being used.  If in the future
the community determines that this feature is required, it can be redesigned and reimplemented at
that time.


Description
-----------

All code related to dynamic reconfiguration will be removed from the code base.  Along with other
internal methods, the user facing API method `reconfigure` will be removed.
