POEM ID: 105  
Title:  Add a "validate" Method to Linear Systems  
authors: rob-hetterich (Rob Hetterich)  
Competing POEMs: None  
Related POEMs:  None  
Associated implementation PR: [#3582](https://github.com/OpenMDAO/OpenMDAO/pull/3582)  

Status:

- [ ] Active
- [x] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


## Motivation

Sometimes after running a model / optimization, there is a desire to run a check on the final values of inputs and outputs. Even if the inputs / outputs are mathematically correct, depending on the values of the inputs and outputs, one may want a component to raise a warning or an error. This helps to inform the modeler if a component is beingn used incorrectly or if they need to adjust their model inputs. Technically, this can already be done by manually doing a get_val after running the model and checking the values of interest. However, certain component models are built to be reusable or are used within a larger tool and it can be cumbersome for a user of that component to have to know to manually add a check whenever they use it. The more flexible approach would be for components and groups to have a method built into the component which can be called to perform a check on their inputs / outputs after the model has run so that they can warn or error to the user of the component.


## Description

I am proposing adding a `validate` method to the base System class. Similar to `setup`, when `run_validation` is run on a model, all of the `validate` methods are called down the model hierarchy to perform any needed validations on the systems making up the model. The validate method should take in the inputs / outputs so that their values can be checked (but not set).




