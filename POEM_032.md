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
Getting scaling right on a large optimization is challenging, 
even when you have a good sense of the relative magnitudes and sensitivities of the DVs, 
objectives, and constraints. 
If you're helping to scale someone else's model or building a new optimization problem from scratch, 
then you may not have a good sense of the problem and proper scaling becomes extremely difficult. 

OpenMDAO should produce a report showing the model values, the scaled values (i.e. as the drive sees them) for all DVs, objectives, constraints. 
It should also include information on the magnitude of the total derivative Jacobian in both 
model and driver-scaled forms. 

Presenting this information in a compact, ordered fashion will assist the user in developing a good scaling scheme for their model. 


Description
-----------

Timing Requirements
===================

The scaling report will include information about the objective, constraints, 
and derivatives, hence `run_model` must be called before generating the report (to make sure those quantities are valid). 
Also, it's critically important that the scaling report be generated after all of the initial values have been set by the user. 

Ideally this feature will be accessible both from a method the user can call on driver, 
or via the OpenMDAO command line. 

When called by a user inside their run-script, the responsibility of correct timing is on them. 
When called by the command line tool, the only way to ensure proper timing would be 
to intercept the call to `run_driver`. 
By the time the user calls `run_driver`, they must have initialized the model to their satisfaction. 

Script API
===========

```
driver.scaling_report(filename=None, jac=True, coloring=True)
```

If no file name is given, output should be reported to standard output

`jac` argument controls if derivatives are included in the scaling report or not. 


`coloring` argument controls if total derivative coloring should be used to filter out known zero parts of the Jacobian from the report. 

Command Line API
================

```
openmdao scaling_report --filename <some name> --no-jac --no-coloring <script>.py 
```

If no filename argument is given, report should go to standard output

The `--no-jac` and `--no-coloring` each turn off their respective features. 
The defaults for these arguments are True in the script interface and most users should want 
both features applied, so it makes sense to make the added arguments to turn them off. 


Report Formatting
=================

Consider a problem with 15 design variables, 10 constraints, and one objective. 
Users have provided values for ref, ref0, upper and lower (for dvs) for some or all of these.
We need to give the user a detailed summary of the problem scaling. 
Keeping in mind that some or all of the dvs, objectives, 
and constraints might be scalar or arrays. 


The scaling report should be formatted like this: 

```
Design Variables
-----------------

                driver (model)                driver (model)   driver (model) 
 name (shape)   value  (value)   ref   ref0    lower (lower)   upper  (upper) 
----------------------------------------------------------------------------
x (1)           1       (10)      10    0      -0.2   (-0.2)   10     (100)    
y (10)         |31.6|  (|31.6|)   1     0      -100   (-100)   100    (100)    

```

Notes: 

- Variables should be sorted in order of lowest to highest driver value (sorting by driver value makes the most sense since this is for scaling, and the driver value is what matters in that context.)
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

                             model    driver  
 (output, input) | (shape) | value  | (value) |
----------------------------------------------------------------------------
f,x                  1       10       (1)            
f,y               (10,10)    |31.6|   (|31.6|)        
     min                        -37   (-37)   
     max                        1e20  (1e20)  

```

Notes: 
    - All names should be given using promoted names
    - Since jacobians are very often matricies, the default should be the min-max view. 
    - The user can request a full printing, in which case the jacobian is flattened and expanded into extra rows. The index of value in the sub-jac will be given in the shape column.




