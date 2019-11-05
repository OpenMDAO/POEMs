POEM ID: 002
Title: New capability for user to send a termination signal to an OpenMDAO process so that SNOPT in pyoptsparse can terminate cleanly.
Authors: [Kenneth-T-Moore]
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
----------
The SNOPT optimizer provides a way to cleanly terminate an optimization by returning a status of -2
or lower from the model function and gradient evaluation functions. This allows for a clean and
graceful exit from optimization. To take advantage of this under a wide range of operating
scenarios (serial, MPI, job queue submission), we need a way to send a signal to a running OpenMDAO
model to tell it to return a -2 to pyoptsparse/SNOPT so that we can terminate cleanly.


Description
-----------

Sending Signals from the OS
===========================
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
=====================================
The Python standard library includes a library [3] for dealing with signals, including a way to
associate a handler function with a particular signal, so that when that signal is detected, the
handler function is called. When this feature is enabled by the user, a handler will be placed
on the expected signal. This handler will raise a new exception `UserRequestedException` that
will be caught in `_objfunc` and `_gradfunc`, where the return code `self.fail` will be set
to -2.


User Interface for Enabling New Capability
============================================
A new option named "user_termination" will be added to the pyOptSparseDriver, with the default
value of False.  When the user sets this to True, the capability to signal a clean termination will
be enabled.

A new option named "user_termination_signal" will be added to the pyOptSparseDriver, with the
default value of `signals.SIGUSR1`.  The user can change this to any other valid signal name or
number.


Changes needed to pyoptsparse
=============================
Unfortunately, mdolab/pyoptsparse will need to be updated to support this upgrade. Presently,
`Optimizer` in pyOpt_optimizer.py squelches the returned error code by turning it into a
strict boolean. This will need to be modified so that a user-requested termination flag
is also passed.  All optimizer wrappers will also need to be modified to expect this new
argument from the masterFunc calls.

Implementation details may need to be worked out with caretakers of pyoptsparse.


References
----------
1. https://en.wikipedia.org/wiki/Signal_(IPC)
2. https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/signal?view=vs-2019
3. https://docs.python.org/3/library/signal.html
4. https://en.wikipedia.org/wiki/Kill_(command)
5. https://slurm.schedmd.com/scancel.html