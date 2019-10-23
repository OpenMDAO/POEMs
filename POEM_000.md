POEM ID: 000  
Title: POEM Purpose and Guidelines   
Poet: justinsgray (Justin S. Gray)   
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A  

Status: Active 

What is a POEM? 
===============
The **p**roposal for **O**penMDAO **e**nhance**m**ent (POEM) is a document that serves to propose a new feature addition, API change, or other modification to the [OpenMDAO code base](https://github.com/OpenMDAO/OpenMDAO). 
A POEM also serves as a record of community discussion on the proposal, 
and records the final decision as to whether or not to accept the proposal. 


Should a POEM contain actual poetry? 
====================================
a real poem needn't be present
but you may find it more pleasant 
to include one in your work
so you get an internet point perk 


POEM Audience 
==============
POEMs will be written by both the OpenMDAO developers and external community users. 
All POEMs will be publicly available and are intended to reviewed by any and all users of the framework. 
Authors should expect to receive comments and suggested changes to their POEMs before they can be reviewed and accepted by the core openMDAO dev team. 

It is expected that discussion on POEMs will be mainly between active users of OpenMDAO and development team. 
However, since POEMs will be publicly available, comments and suggestions may come from anyone. 


Who decides if POEMs are accepted?
==================================

The sole decision making authority regarding the acceptance or rejection of a POEM lies with the core OpenMDAO development team. 
The "Core OpenMDAO Development Team" is defined as the group of developers at NASA Glenn Research Center who are tasked with the curation of the project. 

The Core OpenMDAO Development Team will be referred to as the "Devs" for the rest of this document and for all future POEMs. 


POEM Rules 
==========

    - The author of a POEM, a.k.a the poet, is responsible for its curation. 
    Curation includes addressing relevant comments, integrating community feedback, and changing the state of the POEM from *active* to *requesting decision*.

    - A POEM must have at least one poet, but may have more than one. 
    All poets must be identified in the POEM header by their github username (and optionally their real name in parenthesis). 

    - It is up to the poet's sole discretion which community input to accept and which to reject. 
    Poets are strongly encouraged to seek consensus, to carefully consider feedback, and to incorporate suggestions where possible. 
    However, ultimately the poet gets the final decision. 

    - In the event of conflicting proposals about a specific topic, competing POEMs may be written by different authors. 
    This may happen, for instance, if a poet refuses to incorporate suggestions that another community member finds significant. 
    In this case, both POEMs must explicitly cross reference each other in the `Competing POEMs` line of the POEM header. 
    If you wish to create a competing POEM, it is your responsibility to 
    submit a PR to the original POEM adding your new POEM to their header. 
      
    - When a POEM is in the *active* state, PRs related to it will only be accepted if they come from a poet who is explicitly listed in the POEM header. 

    - When a POEM is in the *requesting decision* state, PRs related to it will only be accepted when the come form a member of the core development team or from one of the PEOM's poets.
    The *requesting decision* state serves as a clear indication that the poet has decided to stop accepting additional input on their POEM. 

    - The Devs are the only people with authority to move a POEM to either the *accepted* or *rejected* state.

    - Regardless a POEM's acceptance or rejection, all reasonable POEMs will be merged to the main repository to keep a record of community discussion. 
    This merge will only occur once the poet has changed the POEM state to *requesting decision*. 
    
    - A POEM may be submitted coincidently with an accompanying pull request (PR) containing an 
    implementation of the proposed feature. 
    Alternatively an accompanying PR may be submitted later, after some initial discussion on the POEM hahappened. 
    It is up to the poet's discretion when to submit a implementation PR to the [OpenMDAO codbase](https://github.com/OpenMDAO/OpenMDAO). 

    - A POEM may be submitted, reviewed (and even potentially accepted) before any code has been written. 
    Contributors are encouraged to submit POEMs before writing code if they are concerned about wasting time on something that would not get accepted. 
    
    - The Devs may elect, at their sole discretion, to accept a POEM without a reference implementation. 
    This situation is expected to be rare, but on occasion my be necessary when a POEM requires massive changes to the code base. 


How can you contribute to another poet's POEM? 
==============================================
You can only contribute to POEMs that are in the *active* state. 
There are two options to contribute to an active POEM: 

1) You can comment on the PR associated with the specific POEM via github's interface. 
This comment may be either a broad comment in the discussion thread, or a direct comment on specific lines of the PR. 
Genearly this can be used to register an opinion or make small suggestions for improvement. 
This type of contribution usually would not warrant recognition as a poet in the header, though the original poet may choose to include you at their sole discretion. 

2) You can submit your own PR to the poets fork, 
which they can choose to accept or not. 
Genearly this would probably entail more significant contribution to the POEM which would likely justify your addition as an additional poet to the POEM. 
You may indicate your preference for recognition by including your username in the header as part of your PR. 

Poets are encouraged to err on the generous side when making decisions about attribution, but generally speaking contributions must be substantial and impactful on the final state of a POEM to warrant recognition. 
While greatly appreciated, editorial improvements (e.g. grammar, spelling, and rewording) do not warrant poet status. 



Allowed POEM States
===================

    - active: POEM has been submitted and is currently being discussed by the community 
    - requesting decision: POEM 
    - accepted: POEM has been accepted by the dev team and an associated PR will be accepted when submitted
    - rejected: POEM has been rejected by the dev team and an associated PR will *NOT* be accepted if it was submitted
    - integrated: The associated PR for an accepted POEM has been merged into the master branch 


When should a POEM include an Implementation PR? 
================================================

While implementation PRs are not strictly requires, in most cases a POEM will not be accepted without one. 
If you are proposing a new feature addition (e.g. a new driver, solver, or component) then an accompanying PR to the [OpenMDAO code base](https://github.com/OpenMDAO/OpenMDAO) will be required before acceptance. 

You are welcome to submit a POEM with out the implementation PR at first, 
especially if you are concerned that it won't be accepted by the Devs. 
It is reasonable to submit a POEM and ask for an initial opinion by the Devs before investing a lot of time and effort into an implementation. 

In some cases, specifically in the case of API changes to existing functionality, 
it is expected that a POEM will be submitted without an accompanying implementation PR. 
Furthermore, the POEM may undergo a lot of discussion and progress all the way to the accepted state without having an implementation PR. 
It is up to the Devs discretion whether or not to request the poet provide an implementation before accepting. 


What if my POEM is rejected?
============================

There are many reasons why a POEM may be rejected, most of which have nothing to do with the proposals merits or value to the community. 
A rejection is not in any way intended to be a commentary on the value of the POEM. 

The Devs are very specifically concerned with the overall maintainability and stability of the code base. 
If a POEM requires new code to be added then the Devs must make a careful consideration as to whether they are willing to take the responsibility of maintenance for that code moving forward. 
If they can't take that responsibility, then they will reject what is otherwise a very good POEM. 

In the case of rejection, if possible, poets are highly encouraged to move their POEM into a stand-alone repository and create an OpenMDAO plugin by listing OpenMDAO as a dependency for their code in the `setup.py` file. 
This will enable other users to install their code and use it, but will avoid having the Devs take responsibility for the code. 

If you have produced a plugin based on a rejected POEM, but at some later date you feel that it should be re-considered for inclusion into the main code-base, then you can re-submit the POEM by changing its state back to *requesting decision*. 
Alternatively, the Devs may choose to revive your POEM at a later date if they feel it is worth reconsidering. 


Submitting a POEM
================
To submit a POEM, fork this repository and add new POEM either as a single markdown file, 
or as a folder with both markdown and images. 
When naming your POEM, assign it the next highest available integer (e.g. 001, 002, 003, etc.). 
Note that all POEMs must start in the **active** state (as indicated in the state line of the POEM template). 
When ready for your POEM to be read, submit a PR to the [main repository][https://github.com/OpenMDAO/Poetry] on the OpenMDAO organization. 

