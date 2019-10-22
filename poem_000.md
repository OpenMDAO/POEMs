POEM ID: 000
Title: POE Purpose and Guidelines 
Author: Justin S. Gray 

Status: Active 


What is a POEM? 
===============
The **P**roposal for **O**penmdao **E**nhance**m**ent (POEM) is a document that serves to propose a new feature addition, API changes, and other signficant modifications to OpenMDAO. 
A POE also serves as a record of community discussion on the proposal, as well as the record of the final decision by the development team as to whether or not to accept the proposal. 


POE Audience 
==============
POEs are intended to be written by both the core OpenMDAO dev team and external community users. 
Once written, a POE will be publicly available and is intended to be read by any and all users of the framework. 
POE authors should expect to receive comments and suggested changes to their specific POE before it acceptance by the dev team. 

It is expected that discussion on POEs will be mainly between active users of OpenMDAO and the core dev team. 
However, since POEs will be publicly available, comments and suggestions may come from anyone. 
It is up to the POE authors discretion which input to accept and which to reject. 


Submitting a POE
================
To submit a POE, fork this repository and add new POE either as a single markdown file, or as a folder with both markdown and images. 
When naming your POE, assign it the next highest available integer (e.g. 001, 002, 003, etc.). 
When ready, submit a PR to the main repository on the OpenMDAO organization. 

POE States
==========

    - active: POE has been submitted and is currently being discussed by the community 
    - accepted: POE has been accepted by the dev team and an associated PR will be accepted when submitted
    - rejected: POE has been rejected by the dev team and an associated PR will *NOT* be accepted if it was submitted
    - integrated: The associated PR for an accepted POE has been merged into the master branch 

POE Rules 
=========

    - The author of the POE is responsible for its curation, which includes the initial 
      submission of the POE as well as integration of comments and feedback from the community 

    - OpenMDAO Dev team is the only group with authority to move a POE out of the `active` state

    - Regardless of final acceptance or rejection, all reasonable POE PRs will be merged 
      to keep a record of community discussion
    
    - A POE may be submitted, reviewed (and even potentially accepted) before any code has been written. 
      Contributors are encouraged to submit POEs before writing code if they are concerned 
      about wasting time on something that would not get accepted. 
    
    - A POE may be submitted coincidently with an accompanying pull request (PR) containing an 
      implementation of the proposed feature. 
      Alternatively an accompanying PR may be submitted later, after some initial discussion on the POE has happened. 
      It is up to the POE authors discretion when to submit a PR with an implementation,
      but in most cases a POE will not be accepted by the dev team without at least a reference implementation. 

    - The dev team may elect, at it discretion, to accept a POE without a reference implementation. 
      This situation is expected to be rare, but on occasion my be necessary when a POE requires massive changes to the code base. 



