POEM ID: 048  
Title: Semistructured Training Data for MetaModel  
authors: justinsgray  
Competing POEMs: N/A     
Related POEMs:   
Associated implementation PR:  

#  Status

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

# Motivation

Semi-structued training data occurs frequently in engineering applications like performance maps for turbine engine performance, propeller performance, aerodyanmic drag, etc. 
A simple example of semistructured training would a mostly structured grid, but where a few data points are missing on one area of the grid. 

Due to the prevalence of this kind of data, it would be valuable to support interpolation of it natively by the existing interpolation component. 

# Description 

The underlying interpolation routines used in MetaModelStructuredComp component already have the ability to process semistructured data, 
but the training data API does not allow for it because it expects fully structured data. 
POEM_048 proposes expansion of this capability to support Semi-structured data as well. 


# Definition of semi-structured data

Semi-structured data consists of nested sets monotonically increasing arrays of input values paired to arbitrary output values (i.e. outputs need not be monotonic)

This is an example of semistructured data with 2 inputs (x,y)  and one output (z): 
```
x = 1
    y = 1, 2, 3, 4
    z = 10, 20, 30, 40
x = 2 
    y = 3, 4, 6
    Z = 60, 80, 120
x = 3
    y = 10, 11
    z = 300, 330
```
Semi-structured is different from structured data, because you do not have a complete grid of training data. 


A structured data set for the same example as above would be: 
```
x = 1
    y = 1, 2, 3, 4, 5, 10, 11
    z = 10, 20, 30, 40, 50, 100, 110
x = 2 
    y = 1, 2, 3, 4, 5, 10, 11
    Z = 60, 80, 100, 200, 220
x = 3
    y = 1, 2, 3, 4, 5, 10, 11
    z = 300, 330, 120, 150, 300, 330
```

## Potential data formats for semi-structured data

Formatting semi-structured data is a bit more difficult than structured data. 
For structured data you need a 1D array for each input variable, and an ND array of training data with each dimension matching the length of one of the input arrays.
```python
# Structured Data inputs
x = [1,2,3]
y = [1,2,3,4,5,10,11]

# can use meshgrid to create a 3D array of test data
X,Y = np.meshgrid(x, y, indexing='ij')
Z = 10*X*Y
```
This format fits easily into NDarrays, matching with how inputs on OpenMDAO components work. 
This is important, because MetaModelStructuredComp offers the ability to have the training data as input to the component, so it could be computed by some upstream part of the model. 
The goal is to retain this feature for semi-structured data as well. 

A simple semi-structured data format is a list-of-lists: 
```python
# Semi-structured data inputs
X = [1,2,3]
Y = [[1,2,3,4], 
     [3,4,5], 
     [10,11]]
# semi-structured data outputs
Z = [[10,20,30,40], 
     [60,80,100], 
     [300, 330]]
inputs=[X,Y]
outputs=[Z,]
```
The list of `inputs` and `outputs` at the end provides the necessary hierarchical information so that you can traverse the input data sets in the correct order. 
Search `X` first then `Y` and for each entry in `X` there should be one entry in `Y`. 
Each entry in `Y` should be matched with an entry in `Z` of the same length. 
This data format is compact, but since the sub-lists are not all of the same length the data doesn't fit into the NDarray paradigm. 
We can use `NAN` to pad out sub-lists so they are all filled and would fit into an NDarray.
```python
# Semi-structured data inputs
input_order=['X','Y']
input_sizes={'X':3, 'Y':[4,3,2]}
X = [1,2,3]
Y = [[1,2,3,4], 
    [3,4,5,np.NAN], 
    [10,11,np.NAN],np.NAN]

# semi-structured data outputs
Z = [[10,20,30,40], 
    [60,80,100,np.NAN], 
    [300, 330,np.NAN]]
```

It is possible to make the input format match the Structured format exactly 
by converting the semi-structured data into a structured format and using `NAN` to pad out the resulting training data arrays. 
This conversion requires that each input dimension be given as a monotonic 1D list that contained all the possible training points from the data set. 
The primary advantage of this data format is that it would allow the MetaModelStructuredComp component to accept semi-structured data with essentially no modifications to its API.
The downside is that this data format is not very human readable/writable.  
```python
x = [1,2,3]
y = [1,2,3,4,5,10,11]

X,Y = np.meshgrid(x, y, indexing='ij')
Z =[[10,20,30,40,NAN,NAN,NAN], 
    [NAN,NAN,60,80,100,NAN,NAN],
    [NAN,NAN,NAN,NAN,NAN,300,330]]
```
However, it would be strait forward to write a utility that could parse a more human readable data format and convert it into the NAN-padded-structured format. 


One last option would be to use a string-name based organization for the data, with hierarchy and index information encoded in the string. 
This would be substantially different from the current MetaModelStructuredComp API, 
but does still match the OpenMDAO input paradigm.
Each string would match up with a single input on the component. 
```python
# Semi-structured data inputs
input_names=['X','Y']
input_sizes={'X':3, 'Y':[4,3,2]}
input_data = {'X_0':[1,2,3], 
                  'X_0:Y_0':[1,2,3,4], 
                  'X_0:Y_1':[3,4,5],
                  'X_0:Y_2':[10,11]
              }
# semi-structured data outputs
output_data ={'X_0:Y_0:Z':[1,2,3,4], 
              'X_0:Y_1:Z':[60,80,100], 
              'X_0:Y_2:Z':[300,330]} 

```
This data format has the advantages of being very human readable and not requiring any NAN entries. 
Its primary disadvantage is that it would require a very different API from the existing MetaModelStructuredComp component. 

# Primary considerations for selecting a data format

## Compute cost of interpolation

The interpolation algorithms must do a large amount of bisection-searching of input arrays to find boundary conditions for any interpolation. 
The performance of these searches impacts the compute cost of interpolation. 
Poor choice of data format could have negative impact on the cost of the searchers. 

## Fixed training data use case

If you have a single fixed set of training data (e.g. a fixed efficiency map for a propeller) that you only need to be able to interpolate on, 
then you only need to provide that data one time during instantiation. 
In this were the only use case, then preference would be given to the most easily worked with data format. 
The data could be stored in a properly formatted text file, and a pointer to that file given to the interpolation component. 

You would not even need to create inputs on the interpolation component boundary for the training data, 
so there would be no concerns about compatibility of the data format and OpenMDAO's input format. 

## Changing training data use case

If the training data is expected to change during an analysis/optimization (e.g. you are computing the training data itself as part of the model) then you do need to consider compatibility with OpenMDAO's input format. 
An example of would be for aircraft sizing when the geometry is changing so you may compute vehicle aerodynamics at a predetermined set of points to fill out the meta-model which is then used as in a trajectory analysis. 
A similar process could be used for generating engine performance data for aircraft sizing, when the engine design itself was part of the design loop. 

In these cases, there is a key step of mux-ing the various training data results into the training data array. 
For structured cases every entry in the training data matrix can be handled with the standard OpenMDAO MuxComponent. 

For semi-structured data, only some of the entries need to be filled, and others need to be set to NaN. Determining which entries need to be filled translates into a tricky connection problem.  
The connection problem could be lessened by the variable naming based data-structure
```python
# Semi-structured data inputs
input_order=['X','Y']
input_sizes={'X':3, 'Y':[4,3,2]}
input_data = {'X_0':[1,2,3], 
                  'X_0:Y_0':[1,2,3,4], 
                  'X_0:Y_1':[3,4,5],
                  'X_0:Y_2':[10,11]
              }
# semi-structured data outputs
output_data ={'X_0:Y_0:Z':[1,2,3,4], 
              'X_0:Y_1:Z':[60,80,100], 
              'X_0:Y_2:Z':[300,330]} 

```
One option would be to offer a semi-structured specific mux component, which could take in the individual data points and then output them in whatever semi-structured mux data format is needed. 

## Value of having one class vs two

When choosing data formats, some consideration should be given to combining both structured and unstructured data into one MetaModel class or if they should be separate classes. 
If they are going to be the same class, then that forces the NAN format for the sake of backwards compatibility: 
```python
x = [1,2,3]
y = [1,2,3,4,5,10,11]

X,Y = np.meshgrid(x, y, indexing='ij')
Z =[[10,20,30,40,NAN,NAN,NAN], 
    [NAN,NAN,60,80,100,NAN,NAN],
    [NAN,NAN,NAN,NAN,NAN,300,330]]
```

However, the difficulty of getting semi-structured data into this format --- even if utilities were provided to translate from a more natural format --- is also a consideration. 
Additionally, there is likely to be some differences in the binary-searches required between structured and semi-structured data due to the presence of NaN values. 

Though one less class for users to have to know about would be nice, the downsides of consolidation outweight the advantages. 

## Semi-structured vs. unstructured interpolation

It is not strictly necessary to support semi-structured data as a separate data format, 
because OpenMDAO already supports an unstructured format that could be used. 
However the unstructured format is less flexible in the kind of interpolations that can be used 
and effectively requires you to put more care into the construction of the surrogate itself. 

Many users find the pure interpolation based results preferable, even though they often offer lower performance, because of their simplicity of use. 
Semi-structured data is capable of being used with the same interpolation routines and hence OpenMDAO should offer this feature. 

# API for MetaModelSemiStructuredComp

## Data format
For ease of human readability and ease of data entry, the simplest text based data format is selected: 
```
inputs = [x,y]
outputs = [z1,z2]
x = 1
    y = 1, 2, 3, 4
    z1 = 10, 20, 30, 40
    z2 = 5, 10, 15, 20
x = 2 
    y = 3, 4, 6
    z1 = 60, 80, 120
    z2 = 30, 40, 60
x = 3
    y = 10, 11
    z1 = 300, 330
    z2 = 150, 165
```
Since this is not valid python code, a semi-structured data parsing utility will be provided that will convert the text file to a semi-structured data object with the following attributes:
```python
# Semi-structured data inputs
input_order=['x','y']
input_sizes={'x':3, 'y':[4,3,2]}
x = [1,2,3]
y = [[1,2,3,4], 
    [3,4,5,np.NAN], 
    [10,11,np.NAN],np.NAN]

# semi-structured data outputs
z1 = [[10,20,30,40], 
     [60,80,100,np.NAN], 
     [300,330,np.NAN]]

z2 = [[5,10,15,20], 
     [30,40,50,np.NAN], 
     [150,165,np.NAN]]
```
This data format allows the compatible APIs for both semi-structured and structured meta models, 
even though the actual data format itself is not the same. 
It also groups all the relevant interpolation data to the left side of every row of data (i.e. NAN padding is only ever used to fill empty space at the end of an array), 
which allows for an efficient bisection search to be done giving efficient interpolation
Finally, it also allows the output data to fit nicely into an NDarray, which makes that data compatible with the OpenMDAO input needs. 

## SemiStructuredMetaModelComp API

The component class, named MetaModelSemiStructuredComp, will have the following APIs: 
``` python
ss_data = om.semi_struct_data_loader('sstruct_data.txt')
interp = om.MetaModelSemiStructuredComp(method='scipy_slinear')

# set up inputs and outputs
interp.add_input('x', 0.0, training_data=ss_data.x, units=None)
interp.add_input('y', 1.0, training_data=ss_data.y, units=None)
interp.add_output('z1', 1.0, training_data=ss_data.z1, units=None)
interp.add_output('z2', 1.0, training_data=ss_data.z2, units=None)

# NOTE: Setting order and sizes is optional. 
#       If not set, is inferred form addition order of inputs. 
#       Setting this allows for error checking of data and makes 
#       the order inputs are declared irrelevant. 
#       It also allows error checking to make sure that expected NAN 
#       values in the training data do not contain non-NAN values.
interp.set_input_metadata(order=ss_data.input_order, sizes=ss_data.input_sizes)

interp.add_output('interp', 1.0, training_data=ss_data.Z, units=None)
```
