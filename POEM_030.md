POEM ID: 030  
Title: User Accessible Complex Step  
authors: [justinsgray] (Justin Gray)   
Competing POEMs: N/A  
Related POEMs:    
Associated implementation PR:    

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


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

Currently, there is a `force_alloc_complex` argument. When true, we allocate the memory needed for complex-step but don't currently expose any API methods that would let the users get to that. One approach would be to just allow set/get when this setup argument is set to true. However, this would cause a modest backwards incompatibility because older models may have turned this one, but then accessed the real values from the getter methods. Thus, their models would start outputing complex values and may break the scripts they have. 

The fix should be fairly easy (adjust the scripts to grab the real parts), 
but we'll need to provide an update-release with a backwards compatibility warning. 

The most common use case that I know of for force_alloc_complex is in writing tests that verify partial derivatives. To make this upgrade painless, the OpenMDAO assert_near_equal method can be updated to handle the case when you are comparing a complex and real value. The only question is how to handle the complex portion. In any existing use case, users will have set purely real values into the model before running. So the outputs will now be complex, but the complex part will be 0. We can compare the real and complex parts separately and just take rms error of them. 


Setting Values 
++++++++++++++

The user sets values using one of two interfaces: 

1) `p['<some_var>'] = <some_val>`
2) `p.set_val('<some_var>', <some_val>)`

In both of these cases, the user should be allowed to pass complex-values into the model. 
Note that complex values are only allowed if the user has passed `force_alloc_complex=True` to the problem `setup` method. 

If the user has not passed the complex allocation flag to setup, and then tries to set a complex value an error should be raised. 

If a user uses the `p.set_val` method to set things, they are allowed to provide a unit. 
If the unit provided in the set call is different than the unit of the variable, then OpenMDAO converts the value for you. 
If a complex value is passed into set_val, and a unit conversion is required based on the unit argument provided, then the unit conversion will apply to *both* the real and complex parts of the value. 
Users will need to be aware of this, since the unit conversion will affect the derivative computed using a complex-step approximation. 


Getting Values 
++++++++++++++

The user gets values in one of three ways

1) `x = p['<some_var>']`
2) `x = p.get_val('<some_var>')`
3) `p.model.list_outputs()`

If `force_alloc_complex=True` is given as an argument to setup, then all of these should report complex values for their outputs. 