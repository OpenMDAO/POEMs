POEM ID:  074  
Title: Suggest variables close in name on failed connection attempt  
authors: joanibal (Josh Anibal)  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: OpenMDAO/OpenMDAO#2681  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

<Note: two space are required after every line of the header to create proper linebreaks in the markdown>


## Motivation
Debugging connections while creating a model are a frequent source of frustration for me as a user. 
Often when I'm debugging I just go into the source and add statements to print out the all the input and output variable names when a connection attempt fails.
This helps me find errors in failed connects resulting from forgotten promotions, capitalization, or typos. 

## Description
This POEM adds suggestions to failed connection errors based on variables with close names.
My suggested approach is the same as what Neil Wu did for some of [our codes](https://github.com/mdolab/baseclasses/pull/32) in the MDOLab.
Use the `get_close_matches` function from the built-in `difflib` to get the suggestions and then append them to the error messages. 
A mockup of this is included in the associated PR.
Below is a comparison of before and after the proposed change

### Before
```
NameError: <model> <class Top>: Attempted to connect from 'mesh_aero.x_aero0' to 'cruise.x_aero0', but 'cruise.x_aero0' doesn't exist.
```


### After
```
NameError: <model> <class Top>: Attempted to connect from 'mesh_aero.x_aero0' to 'cruise.x_aero0', but 'cruise.x_aero0' doesn't exist. Perhaps you ment to connect to one of the following inputs:['cruise.x_aero', 'cruise.x_struct0', 'cruise.aero_post.aoa']
```






