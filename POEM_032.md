POEM ID: 032  
Title: Detailed Driver Scaling Report  
authors: [justinsgray]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR:  

Status:  

- [ ] Active  
- [ ] Requesting decision  
- [x] Accepted  
- [ ] Rejected  
- [ ] Integrated  



Motivation
----------
Getting scaling right on a large optimziation is challenging, 
even when you have a good sense of the problem. 
Most users --- especially ones who are debugging other peoples opts ---
don't have a complete picture of all the DVs, objectives, and constraints. 

The framework should be able to produce a report showing the model values and the scaled values (i.e. as the drive sees them) for all DVs, objectives, constraints. 


Description
-----------

This new feature should be accessible both from a method the user can call on driver, 
or via the OpenMDAO command line. 

Because the scaling report will include information about the objective, constraints, 
and potentially derivatives it will need to be run before generating the report. 
So the driver method will have to call run_driver once. 
This call to run_driver should not trigger any case recording (this might be challenging...)


Consider a problem with 15 design variables, 10 constraints, and one objective. 
Users have provided values for ref, ref0, upper and lower (for dvs) for some or all of these.
We need to give the user a detailed summary of the problem scaling. 
Keeping in mind that some or all of the dvs, objectives, 
and constraints might be scalar or arrays. 


The scaling report should be formatted like this: 

```
Design Variables
-----------------

                model  driver                 model driver    model  driver 
 name (shape) | value  (value) | ref | ref0 | lower (lower) | upper (upper) | 
----------------------------------------------------------------------------
x (1)           10      (1)      10     N/A     -20   (-0.2)   100    (10)    
y (10)         |31.6|   (|31.6|)  1     N/A     -100  (-100)   100    (100)    

```

Notes: 

- Array values should be shown as the 2-norm of the array
- Its likely that  the value will be an array, but the ref/ref0 or upper/lower will be scalar. 
  only the array values should be shown as a norm. 
- There will be an option for print-arrays, in which case arrays are flattened and expanded vertically. 
  even though the variable is flattened to show, the shape note should contain the correct shape 
- There will be an option to print the min/max values for arrays (rather than show the full array). 
  The associated ref/ref0 upper/lower will match up with the index of the min/max
- There will be separate sections for design variables, objectives, constraints. 
- The constraint section will add a column idenifying the type (upper/lower/equal). 
  It will also have columns for the current value, along with the constraint value shown in both model and driver scaled values. 
- If a constraint is specified with both lower and upper, then separate rows will output for each argument. 
- At the start of each section should be a summary table which gives the minimum and maximum value based on driver scaled quantities. 


The format when arrays are fully expanded will look like this
```
Design Variables
-----------------

                model  driver                 model driver    model  driver 
 name (size)  | value  (value) | ref | ref0 | lower (lower) | upper (upper) | 
----------------------------------------------------------------------------
x (1)           10      (1)      10     N/A     -20   (-0.2)   100    (10)    
y (10)          10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    
                10      (10)      1     N/A     -100  (-100)   100    (100)    

```


The format when arrays are shown as min/max
```
Design Variables
-----------------

                model  driver                 model driver    model  driver 
 name (size)  | value  (value) | ref | ref0 | lower (lower) | upper (upper) | 
----------------------------------------------------------------------------
x (1)           10      (1)      10     N/A     -20   (-0.2)   100    (10)    
y (10)         |31.6|   (|31.6|)  1     N/A     -100  (-100)   100    (100)    
  min           10      (10)      1     N/A     -100  (-100)   100    (100)    
  max           1000    (100)     1     N/A     -100  (-100)   100    (100)    
```

In addition to the display of the values, There will be an option to include derivative information as a separate section. 
The derivative section will be formatted like this: 

```
Jacobian
-----------------

                             model  | driver  
 (output, input) | (shape) | value  | (value) | ref | ref0 |
----------------------------------------------------------------------------
f,x                  1       10       (1)        10    N/A     
f,y               (10,10)    |31.6|   (|31.6|)   1     N/A       
     min                        -37   (-37)   
     max                        1e20  (1e20)  

```

Notes: 
    - Since jacobians are very often matricies, the default should be the min-max view. 
    - The user can request a full printing, in which case the jacobian is flattened and expanded into extra rows. 
      The index of value in the sub-jac will be given in the shape column.




