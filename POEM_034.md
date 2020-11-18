POEM ID: 034  
Title:  Units library function to simplify units.  
authors: Kenneth-T-Moore (optional real name)  
Competing POEMs: [list any other POEMs which are incompatible with this one]  
Related POEMs: [list any other POEMs which are related (but still compatible) with this one]  
Associated implementation PR:

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [x] Rejected
- [ ] Integrated

Rejecting this POEM.  This feature will be added to the OpenMDAO issues, but not as a part of the public API.


## Motivation

In Dymos, sometimes we take an existing openmdao variable and create a new one that contains the time
derivative or integral of that variable. To do so, we need to also differentiate or integrate the units by multiplying
or dividing by the time unit. This can create unit strings that are not simplified (e.g., "m/s*s"). This
POEM proposes a units library function that we can call to clean those up.


## Description

This POEM proposes a new method:

   new_unit_str = simplify_unit(old_unit_str)

'ft/s*s' returns 'ft'
'm/s*s' returns 'm'
's/s' returns None

If possible:
'J/s*s' returns 'W'

Care should be taken to make sure that units don't get converted to their base units (i.e., 'ft' -> 'm').

