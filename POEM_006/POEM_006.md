POEM ID: 003  
Title: Re-work the user experience in the N2 diagram  
Authors: [hschilling]
Competing POEMs: [N/A]  
Related POEMs: [N/A]  
Associated implementation PR:

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
==========
The primary motivations for this POEM are:

* The N2 user interface currently is limited in the number of operations that can be applied to systems. Only two
operations can be done via left and right click. These let the user do zooming and collapsing, respectively. There
is an need to let users do additional operations such as getting metadata on a system. The UI has
to be updated to enable that.
* The current toolbar does not make it obvious what capabilities exist. This is due to icons that don't reflect the
function and also the grouping of buttons is less than ideal.
* Screen real estate is an issue. Ideally the user could see the GUI controls (e.g. the toolbar), the N2 diagram,
and the legend all without scrolling. That is currently not possible for even medium-sized models.
* Additional N2 features need to be considered for future development. For example, there was some talk about
 merging the connection viewer with N2, and/or providing more info about connections, like units.

Description
===========

This POEM proposes the following changes:

* Add to the toolbar a way to choose modes for left-click and double-click. Applications like Photoshop use this kind
of way to interact with items in the app. This could be done using buttons and/or keyboard shortcuts
* Enable a contextual menu using right-click to let the user select additional operations
on the system such as displaying metadata about the system
* Explore different options for the layout of the major elements of the diagram: N2 diagram, toolbar, and legend. 
Options include:
    * Put the toolbar on the left
    * Have the toolbar frozen on the top so when the user scrolls on the page, the toolbar is always present
* Research and draw inspiration from existing applications with toolbars such as Microsoft Office apps and Photoshop

![toolbar with graphic and text buttons](/POEM_006/toolbar_with_graphic_and_text_buttons.png)

* Redesign many of the icons in the toolbar and/or include both an icon and text in the button
* Use card sorting with team members and key users to group buttons on toolbar

Prototypes and Mockups
----------------------
A [prototype](./n2_prototype_from_workshop.html) was created for the OpenMDAO Workshop that showed having buttons
to change modes and also having a right-click contextual menu. The prototype shows 3 different Modes: 
collapse mode, zoom mode, tooltip mode. 

![workshop button mode mockup](/POEM_006/workshop_mockup_mode_buttons.png)

Right-click offered the user the option to Collapse, and Edit File, as examples.


References
----------
1. Ideas from 2019 summer intern UX designer, Sophia Hamed-Ramos
