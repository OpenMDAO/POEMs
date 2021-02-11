POEM ID: 032  
Title: Detailed Driver Scaling Report  
authors: [justinsgray, Eliot Aretskin-Hariton]    
Competing POEMs: N/A   
Related POEMs: N/A  
Associated implementation PR:  

Status:  

- [ ] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [x] Integrated  



# Motivation

Getting scaling right on a large optimization is challenging, 
even when you have a good sense of the relative magnitudes and sensitivities of the DVs, 
objectives, and constraints. 
If you're helping to scale someone else's model or building a new optimization problem from scratch, 
then you may not have a good sense of the problem and proper scaling becomes extremely difficult. 

OpenMDAO should produce a report showing the model values, the scaled values (i.e. as the driver sees them) for all DVs, objectives, constraints. 
It should also include information on the magnitude of the total derivative Jacobian in both 
model and driver-scaled forms. 

Presenting this information in a compact and ordered fashion will assist the user in developing a good scaling scheme for their model. 


# Description


## Timing Requirements


The scaling report will include information about the objective, constraints, 
and derivatives, hence `run_model` must be called before generating the report (to make sure those quantities are valid). 
Also, it's critically important that the scaling report be generated after all of the initial values have been set by the user. 

Ideally this feature will be accessible both from a method the user can call on driver, 
or via the OpenMDAO command line. 

When called by a user inside their run-script, the responsibility of correct timing is on them. 
When called by the command line tool, the only way to ensure proper timing would be 
to intercept the call to `run_driver`. 
By the time the user calls `run_driver`, they must have initialized the model to their satisfaction. 

NOTE: Since scaling only applies to continuous variables, no discrete variable information will be given in the scaling report. 


## Scaling Report File Format


an HTML file containing the data, and a nicely formatted output is desirable. 
This will allow for a modular report that can be shared between users (i.e. the html file can be emailed without the rest of the model itself) while retaining its interactive features. 
The portability of the html file has proven valuable for the N2 diagram, and so we seek to re-use the concept here. 
Users looking for help with scaling will probably share this file with others, so portability is important. 


## Script API


```
driver.scaling_report(filename='driver_scaling_report.html', jac=True)
```

If no file name is given, the default is "driver_scaling_report.html". 

`jac` argument controls if derivatives are included in the scaling report or not. 

NOTE: If total derivative coloring has been turned on by the user, 
then the coloring/sparsity will automatically be applied to gray out any known-zero values in the Jacobian. 

## Command Line API


```
openmdao scaling_report --filename <some name> --no-jac <script>.py 
```

If no filename argument is given, report should dump to default name of `driver_scaling_report.html`

The `--no-jac` turns off Jacobian printing. 
The defaults is True in the script interface and most users should want 
to see derivative information, so it makes sense to have the argument used to turn it off.


## Report Format

Equations should be formulated using mathjax. 
Scaling process summary should be included in the report output, but collapsed.
We need to make a clear indication that they can click it to get more details.


### Scaling Process


The top of every report should include a short summary of how scaling is being applied. 
This is a short bit of math and text that is fixed, and simply explains how to convert between model and driver scaled values.

All scaling in OpenMDAO results in the following linear transformation:

Variable_{driver} = m * Variable_{model} + b

The computed values for m and b depend on how you specify the scaling, and whether or not you specify units that the driver sees which are different from the units in the model. 

#### If you use driver units 
If your model variable is in units of `m` and you choose to use `cm` for the driver value then you have 
a `unit_factor` of 100. 
This conversion is done before anything else. 
All other scaling is done relative to the driver-unit values. 
If your model value was 5.2 meters, then the driver value is 520 centimeters. 
You would then give ref/ref0 or scaler/adder relative to that. 

In general, unit conversions can include both a multiplicative factor and an offset (thank you, Celsius to Fahrenheit)
Given a variable from the model (x_{model}), the unit converted value (x_{unit}) is computed by 

x_{driver} = unit_factor * (x_{model} + offset)

#### If you use ref/ref0: 

The `ref`and `ref0` values represent the model values that will get scaled to 1 and 0 respectively. 

1 = m * (ref + b)
0 = m * (ref0 + b)

This gives the following for m/b: 

b = -ref0
m = 1/(ref - ref0)


#### If you use scaler/adder: 
You are specifying the slope/offset for the scaling directly. 
b = adder
m = scaler 


#### Full unit scaling equation

All of the scaling combined gives a linear map between the driver scaled value (x_{driver scaled}), the unit scaled value (x_{unit}), and the actual model value (x_{model}). 

x_{driver} = m * (unit_factor * (x_{model} + offset) + b)

x_{driver} = [m * unit_factor] * (x_{model} + offset + b/unit_factor)

So the overall scaler is [m * unit_factor] and the overall adder is [offset + b/unit_factor]. 


### Scaled Value Summary


NOTES: Consider a problem with 15 design variables, 10 constraints, and one objective. 
Users have provided values for ref, ref0, upper and lower (for dvs) for some or all of these.
We need to give the user a detailed summary of the problem scaling. 
Keeping in mind that some or all of the dvs, objectives, 
and constraints might be scalar or arrays. 


The scaling report should be formatted like this: 

```
Design Variables
-----------------

                driver                 (model                                              
 name (shape)   value                   value)                  ref   ref0   scaler adder   lower     upper
-------------------------------------------------------------------------------------------------------------
x (1)           1     <driver units>    (10 <model units>)       10    0         x     x       -0.2      10     
y (10)         |31.6| <driver units>    (|31.6| <model units>)   1     0         x     x       -100      100    

```

Notes: 

- user should be able to sort on either the name, driver value, or model value columns
- Array values should be shown as the 2-norm of the array
- If the value is an array, but the ref/ref0, scaler/adder, or upper/lower will be scalar. 
  only the array values should be shown as a norm. 
- There will be an option for print-arrays, in which case arrays are flattened and expanded vertically. 
  even though the variable is flattened to show, the shape note should contain the correct shape 

- There will be separate sections for design variables, objectives, constraints. 
- The constraint section will add a column idenifying the type (upper/lower/equal). 
- If a constraint is specified with both lower and upper, then separate rows will output for each argument. 



If the variable is an array, user can click something to cause it to expand. 
Baseline thinking is that it expands down like this: 
```
Design Variables
-----------------

                driver           index   (model                                  
 name (size)  | value                     value)                    | ref | ref0 | scaler  adder lower  upper 
-------------------------------------------------------------------------------------------------------------
x (1)            1 <driver units>          (10 <model units>)        10    0        x     x     -0.2   100   
y (10)           10<driver units>  0       (10 <model units>)        1     0        x     x     -100   100   
                 10                1       (10)                      1     0        x     x     -100   100   
                 10                2       (10)                      1     0        x     x     -100   100   
                 10                3       (10)                      1     0        x     x     -100   100   
                 10                4       (10)                      1     0        x     x     -100   100   
                 10                5       (10)                      1     0        x     x     -100   100   
                 10                6       (10)                      1     0        x     x     -100   100   
                 10                7       (10)                      1     0        x     x     -100   100   
                 10                8       (10)                      1     0        x     x     -100   100   
                 10                9       (10)                      1     0        x     x     -100   100   

```


### Scaled Jacobian Summary 

There is a lot of data in the Jacobian, and a text based format is to difficult to use for this.
Instead, we'll use a matrix-diagram based view that uses color to indicate order of magnitude. 

![Proposed Jacobian View](POEM_032/Jacobian_0.png)


Here there is one box for each sub-jac in the total derivative Jacobian (i.e. each of/w.r.t pair). 
Each block is given a single color, regardless of whether it is scalar or matrix sub-jac. 
The color is computed based on the order of magnitude of the sub-jac. 
From a scaling perspective the sign of the subjac is not critical, only the order of magnitude. 
So we can use the norm of the entire sub-jac like this: `np.log10(np.linalg.norm(<value>))`. 

The principal challenge with taking a log10 is that any sub-jacs that are exactly zero will get turned into infinity. 
To handle that we'll use a simple clipping process that replaces the infinities with the smallest order of magnitude otherwise seen. 



```python 
import numpy as np
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib import pylab as plt
Jac = np.array([[1e-6, 0, 1e6], [1, -1e10, -1e-4]])

Jac_norm = np.abs(Jac)
log_Jac = np.log10(Jac_norm)

finite_log_Jac = log_Jac[np.isfinite(log_Jac)] 
min_log_jac = np.min(finite_log_Jac)
max_log_jac = np.max(finite_log_Jac)

# check if the order of magnitude is larger on the positive or negative side
CAP = np.abs(min_log_jac)
if max_log_jac > -min_log_jac:
    CAP = max_log_jac

# set any zero values --- which result in inf when you take the log --- to the -CAP
finite_log_Jac = log_Jac.copy()
finite_log_Jac[np.isinf(finite_log_Jac)] = -CAP

normer = Normalize(-CAP, CAP)
cmapper = cm.ScalarMappable(norm=normer, cmap='RdBu_r')
color_jac = cmapper.to_rgba(finite_log_Jac)

plt.imshow(color_jac, )    
plt.show()
```

If sparsity information is used then all known zero values will be grayed out. 
So its only any non-zero values, that happen to be incidentally zero that will get a color assigned. 
If no sparsity information is used, all sub-jacs will get a color assigned based on the order of magnitude. 


Notes: 
    - All labels should be made using promoted namess
    - Grayed out boxes represent empty data in the sparse matrix (i.e. known 0 values). 
      These will only be present when coloring/sparsity data is available. 
      If the total Jacobian is dense, all entries will be colored based on their values. 
    - User should be able to select if they want to see the jacobian in driver centric or model centric values. 


#### Interactive feature 
If the user clicks on any the sub-jac boxes, the actual norm of the value of the sub-jac should be shown in a dialog box below the matrix diagram. 
In addition, a sub-jac diagram should be shown with the log10(abs) of every entry in the sub-jac. 

The color scale for the sub-jac should be based on the min/max values of the full Jacobian (i.e. don't rescale the color map based on the local min/max of that sub-jac)

Similar to the total jac, if sparsity information is available, any known-zero values should be grayed out. 






