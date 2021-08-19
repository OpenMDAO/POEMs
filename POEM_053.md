POEM ID: 053  
Title: Make src_indices behave in the same way as indices applied to a normal numpy array  

Authors: [naylor-b, swryan]  

Competing POEMs: N/A  

Related POEMs: N/A  

Associated implementation PR: #2212  

Status:  

- [ ] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [x] Integrated  


## Motivation  

Currently, indices defined for design vars and constraints behave in the same way that indexing into a numpy array behaves,
but src_indices allows a different syntax where the indices are defined as a possibly nested list of tuples where tuples of
length 'n' indicates that the array being indexed is of dimension 'n'. The equivalent numpy indexing syntax would be a tuple
of index arrays, one for each dimension of the array being indexed.  


## Description  

The goal is to make src_indices behave (like design var and constraint indices) in the same way as indices applied to a normal
numpy array. 

A new argument, `new_style_idx`, will be added to functions that also take a `src_indices` argument (`connect()`, 
`promotes()`, `add_input()`). It will initially default to `False` for backward compatibility, but this will result in a
deprecation warning for any `src_indices` arrays with ndim > 1. 

When `new_style_idx` is True, `src_indices` will use numpy compatible indexing.  The implementation will convert all 
`src_indices` to the new style for execution until the depreaction is removed.

