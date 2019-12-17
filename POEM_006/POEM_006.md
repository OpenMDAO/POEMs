POEM ID: 003
Title: Re work the user interaction in the N2 diagram
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
The SNOPT optimizer provides a way to cleanly terminate an optimization by returning a status of -2
or lower from the model function and gradient evaluation functions. This allows for a clean and
graceful exit from optimization. To take advantage of this under a wide range of operating
scenarios (serial, MPI, job queue submission), we need a way to send a signal to a running OpenMDAO
model to tell it to return an error code  to pyoptsparse/SNOPT so that we can terminate cleanly.


Description
===========

Look at Sophia's document.

Mockups

if we can have a prototype of our the new UI, then thats probably a good place to start
we had decided on a hybrid approach. A tool-bar for choose the mode for the left-click and double-click. ( like Photoshop)
Then a right-click menu that holds functionality (edited)

what kind of functionality?  "info" is one (size, value, units, etc). "Collapse/expand" is another (edited)

More space for legend.

Better buttons.

Currently:

- left click zooms into a system
- right click collapses
-

Put toolbar on the left.

Having the toolbar/header remain on the top but “stick” so that when you scroll on the
page, the bar is always present.

Use card sorting for team members who work on this project.
Include each icon from the toolbar and have each user label what they believe the icon
does.
This is a tool to recognize the effectiveness of the current icons/tool bar to promote
new changes.
They can then be recategorized and tools that aren’t used can be eliminated.


The mockup we did for the workshop had





Sending Signals from the OS
---------------------------
Unix provides a selection of signals [1] that are used for interprocess communication. Microsoft
Windows also provides a smaller set of signals [2] for the same purpose. The discussion here will
focus on Unix signals, as these cover Unix and OSX systems.  Many of the signals already have
defined behavior, such as SIGINT which interrupts execution, SIGTERM which terminates the
process, and SIGSTP which temporarily suspends execution.

Unix provides the `kill` [4] command, which can be used to send any signal to any process.
Similarly, job queue submission systems also provide a way to forward a specified signal to
all processes in the job (e.g., Slurm [5] and PBS [6])

It is important to check how an MPI implementation handles signals as well. For example, OpenMPI
forwards SIGUSR1 and SIGUSR2 to all processes, while HPE MPT does not forward those signals, but
does forward SIGURG.  Because the signal forwarding behavior is different depending on operating
system, mpi implementation, and scheduler, the user must retain the ability to choose which
signal will be used to initiate clean termination.  A reasonable default value is SIGUSR1.


Handling Signals in pyOptSparseDriver
-------------------------------------
The Python standard library includes a library [3] for dealing with signals, including a way to
associate a handler function with a particular signal, so that when that signal is detected, the
handler function is called. When this feature is enabled by the user, a handler will be placed
on the expected signal. This handler will raise a new exception `UserRequestedException` that
will be caught in `_objfunc` and `_gradfunc`, where the return code `self.fail` will be set
to -2.


User Interface for Enabling New Capability
------------------------------------------
A new option named "user_terminate_signal" will be added to the pyOptSparseDriver, with the
default value of `signals.SIGUSR1`.  The user can change this to any other valid signal name or
number. The user can also set it to False to prevent the addition of any handlers.


Changes needed to pyoptsparse
-----------------------------
This POEM is tied to release 1.1 of pyoptsparse.

In pyoptsparse 1.1, The `Optimizer` class was upated to allow a value of 2 to be passed back
to the SNOPT callback function wrapper.


References
----------
1. https://en.wikipedia.org/wiki/Signal_(IPC)
2. https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/signal?view=vs-2019
3. https://docs.python.org/3/library/signal.html
4. https://en.wikipedia.org/wiki/Kill_(command)
5. https://slurm.schedmd.com/scancel.html
