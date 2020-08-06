POEM ID: 014
Title: Removal of XDSM viewer to be replaced by third-party plugin
Authors: @robfalck
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: #1240  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

OpenMDAO developers are accepting this without discussion.

Motivation
==========

Now that OpenMDAO has better support for third-party plugins, we are
removing the XDSM viewer from OpenMDAO.  It is a significant code base
and best maintained by the original developers.


Description
===========

XDSM generation will no longer be available via OpenMDAO command line
or functions unless they install the third party plugin.

Users should use the plugin available at https://github.com/onodip/OpenMDAO-XDSM

References
----------

N/A
