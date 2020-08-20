POEM ID: 000  
Title: POEM Purpose and Guidelines   
Author: justinsgray (Justin S. Gray)   
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

What is a POEM? 
===============
The **p**roposal for **O**penMDAO **e**nhance**m**ent (POEM) is a document that serves to propose a new feature addition, API change, or other modification to the [OpenMDAO codebase](https://github.com/OpenMDAO/OpenMDAO). 
A POEM also serves as a record of community discussion on the proposal, 
and documents the final decision as to whether or not to accept the proposal. 


POEM Audience 
==============
POEMs will be written by both the OpenMDAO developers and external community users. 
All POEMs will be publicly available and are intended to be reviewed by any and all users of the framework. 
Authors should expect to receive comments and suggested changes to their POEMs before they can be reviewed and accepted by the core openMDAO dev team. 

It is expected that discussion on POEMs will be mainly between active users of OpenMDAO and the development team. 
However, since POEMs will be publicly available, comments and suggestions may come from anyone. 


Who decides if POEMs are accepted?
==================================

The sole decision making authority regarding the acceptance or rejection of a POEM lies with the core OpenMDAO development team. 
The "Core OpenMDAO Development Team" is defined as the group of developers at NASA Glenn Research Center who are tasked with the curation of the project. 

The Core OpenMDAO Development Team will be referred to as the "Devs" for the rest of this document and for all future POEMs. 


POEM Rules 
==========

- The author of a POEM, is responsible for its curation. 
Curation includes addressing relevant comments, integrating community feedback, and changing the state of the POEM from *active* to *requesting decision*.

- A POEM must have at least one author, but may have more than one. 
All authors must be identified in the POEM header by their github username (and optionally their real name in parentheses). 

- It is up to the author's sole discretion which community input to accept and which to reject. 
Authors are strongly encouraged to seek consensus, to carefully consider feedback, and to incorporate suggestions where possible. 
However, ultimately the author makes the final decision. 

- In the event of conflicting proposals about a specific topic, competing POEMs may be written by different authors. 
This may happen, for instance, if an author refuses to incorporate suggestions that another community member finds significant. 
In this case, both POEMs must explicitly cross reference each other in the `Competing POEMs` line of the POEM header. 
If you wish to create a competing POEM, it is your responsibility to 
submit a pull request (PR) to the original POEM adding your new POEM ID to their header. 
  
- When a POEM is in the *active* state, PRs related to it will only be accepted if they come from an author who is explicitly listed in the POEM header. 

- When a POEM is in the *requesting decision* state, PRs related to it will only be accepted when they come from a member of the core development team or from one of the POEM's authors.
The *requesting decision* state serves as a clear indication that the author has decided to stop accepting additional input on their POEM. 

- The Devs are the only people with authority to move a POEM to either the *accepted* or *rejected* state.

- Regardless a POEM's acceptance or rejection, all reasonable POEMs will be merged to the main repository to keep a record of community discussion. 
This merge will only occur once the author has changed the POEM state to *requesting decision*. 

- A POEM may be submitted coincidently with an accompanying PR to the [OpenMDAO codebase](https://github.com/OpenMDAO/OpenMDAO) containing an 
implementation of the proposed feature. 
Alternatively, an accompanying PR may be included in the POEM later, after some initial discussion on the POEM has happened. 
It is up to the author's discretion when to submit an implementation PR, but when the PR is made it should be noted in the `Associated implementation PR` field of the POEM header. 

- A POEM may be submitted, reviewed, and potentially accepted before any code has been written. 
Contributors are encouraged to submit POEMs before writing code if they are concerned about wasting time on work that would not get accepted. 

- The Devs may elect, at their sole discretion, to accept a POEM without a reference implementation. 
This situation is expected to be rare, but on occasion may be necessary when a POEM requires significant changes to the codebase. 


How can you contribute to another author's POEM? 
==============================================
You can only contribute to POEMs that are in the *active* state. 
There are two options to contribute to an active POEM: 

1) You can comment on the PR associated with the specific POEM via github's interface. 
This comment may be either a broad comment in the discussion thread, or a direct comment on specific lines of the POEM. 
Generally this can be used to register an opinion or make small suggestions for improvement. 
This type of contribution usually would not warrant recognition as an author in the header, though the original author may choose to include you at their discretion. 

2) You can submit your own PR to the authors fork, 
which they can choose to accept or not. 
Generally this would entail more significant contribution to the POEM which may justify your attribution as another author in the POEM's header. 
You may indicate your preference for attribution by including your username in the header as part of your PR. 

Authors are encouraged to err on the generous side when making decisions about attribution, but generally speaking, contributions must be substantial and impactful on the final state of a POEM to warrant recognition. 
While greatly appreciated, editorial improvements (e.g. grammar, spelling, and rewording) do not warrant author status. 



Allowed POEM States
===================

    active: POEM has been submitted and is currently being discussed by the community 
    
    requesting decision: POEM is ready to be reviewed by the Devs
    
    accepted: POEM has been accepted by the dev team and the associated PR will be accepted when submitted
    
    rejected: POEM has been rejected by the dev team and the associated PR will *NOT* be accepted if it was submitted
    
    integrated: The associated PR for an accepted POEM has been merged into the master branch 


When should a POEM include an implementation PR? 
================================================

While implementation PRs are not strictly required, they are strongly encouraged. 
Most POEMs will not be accepted without one. 
If you are proposing a new feature addition (e.g. a new driver, solver, or component) then an associated implementation PR to the [OpenMDAO codebase](https://github.com/OpenMDAO/OpenMDAO) will very likely be required before acceptance. 

You are welcome to submit a POEM without the implementation PR at first, 
especially if you are concerned that it won't be accepted by the Devs. 
It is reasonable to submit a POEM and ask for an initial opinion by the Devs before investing a lot of time and effort into an implementation. 

In some cases, such as API changes to existing functionality, 
it is acceptable that a POEM be submitted without an associated implementation PR. 
Furthermore, a POEM may undergo a lot of discussion and modification all the way to the accepted state without having an implementation PR. 
It is up to the Devs sole discretion whether or not to insist that the author provide an implementation before accepting a POEM. 


What if my POEM is rejected?
============================

In some cases a POEM may be rejected despite being well thought out, well written, and offering significant value to the community. 
A rejection is not in any way intended to be a commentary on the value of the POEM. 

The Devs are specifically concerned with the overall maintainability and stability of the codebase. 
If a POEM requires new code to be added, then the Devs must make a careful consideration as to whether they are willing to take the responsibility for maintenance for that code moving forward. 
If they do not feel they can take that responsibility, then they will reject what is otherwise a very good POEM. 

In the case of rejection, if possible, authors are highly encouraged to move their work into a separate python package in a stand-alone repository that lists OpenMDAO as a dependency in the `setup.py` file. 
This will create an OpenMDAO plugin that will enable other users to install their code and use it, but will avoid having the Devs take responsibility for the code. 

If you have produced a plugin based on a rejected POEM, but at some later date you feel that it should be re-considered for inclusion into the main codebase, then you can re-submit the POEM by changing its state back to *requesting decision*. 
Alternatively, the Devs may choose to revive your POEM at a later date if they feel they can now support the feature in the core codebase. 


Submitting a POEM
================
To submit a POEM, fork this repository and add new POEM either as a single markdown file, 
or as a folder with both markdown and images. 
When naming your POEM, assign it the next highest available integer (e.g. 001, 002, 003, etc.). 
Note that all POEMs must start in the **active** state (as indicated in the state line of the POEM template). 
When ready for your POEM to be read, submit a PR to the [main repository](https://github.com/OpenMDAO/POEMs) on the OpenMDAO organization. 

