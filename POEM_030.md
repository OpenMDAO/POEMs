POEM ID: 030  
Title: User Accessible Complex Step  
authors: [justinsgray] (Justin Gray)   
Competing POEMs: N/A  
Related POEMs:    
Associated implementation PR: #1777   

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------
Some users may want to complex-step the models manually, by passing complex values into the `__set_item__` and `set_val` methods.
This can be useful for debugging, when they want to check a specific index of a specific variable,
potentially adding debug printing in their components to help.
Having to rely on the check_partials and check_totals in this kind of debug situation is somewhat challenging,
and it would be better to let them call set_val and run_model on their own.
Another potential use case is when using OpenMDAO as a black-box, integrating into some high level code.
If that code wants to complex-step its black-boxes, then the user needs access to a means of passing the complex values down into the model.


Description
-----------

OpenMDAO already supports complex-step in model execution. We don't provide the user a way to access that feature for manual execution though. What is needed is some way for the user to pass in complex values and then see the complex outputs.

We propose a new `Problem` method "set_complex_step_mode(active)". When the "active" argument is True, OpenMDAO enables complex-step mode, and the user can set inputs and get outputs that are complex numbers.


Running in Complex Mode
+++++++++++++++++++++++

The user turns on complex step mode.

`p.set_complex_step_mode(True)`

Now, the user can set values using either of two interfaces:

1) `p['<some_var>'] = <some_val>`
2) `p.set_val('<some_var>', <some_val>)`

These values can be complex.  The user can now call `run_model` and the model will carry the complex numbers through the entire calculation. Note that the model must be complex-safe so that no errors or conversion to real occur unexpectedly. Also, when the model is under a complex step, you cannot run the driver or compute/check total derivatives.

Once the model has been run, the user can get values in three ways:

1) `x = p['<some_var>']`
2) `x = p.get_val('<some_var>')`
3) `p.model.list_outputs()`

The values returned by these methods will all be complex if the model was executed in complex step mode.


Returning to Floating Point Mode
++++++++++++++++++++++++++++++++

Once the complex step is complete, the model can be returned to normal by:

`p.set_complex_step_mode(False)`

Now, all inputs and outputs are floating point numbers.