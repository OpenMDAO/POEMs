POEM ID: 063  
Title: Allow multiple responses on a single variable  
authors: @robfalck  
Competing POEMs:  
Related POEMs:  
Associated implementation PR: [#2473](https://github.com/OpenMDAO/OpenMDAO/pull/2473)  

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


## Motivation

OpenMDAO currently stores design variables and responses in dictionaries that are keyed by the variable path.
This prevents users from adding multiple constraints/objectives to different indices of the variable if it is an array.

## Proposed solutions

Handling constraints internally is currently done through a dictionary keyed by variable name.
To allow multiple constraints on a single variable breaks this storage assumption.
The design team considered three paths:

1. change the storage data structure for responses

This is a significant change in the codebase.
In the interest of keeping the codebase stable, we decided not to pursue this path.

2. key the response dictionary on both name and indices

The biggest drawback to this approach is that indices may be a long list of integers that wouldn't lend itself to being keys in a dictionary.

3. allow the user to specify an 'alias' for responses

This option accommodates the requirements and has the smallest impact on the existing codebase.

## The `alias` option for responses

- Methods `add_constraint`, `add_objective`, and `add_response` will now have an optional `alias` argument that defaults to `None`.
- When `alias` is `None`, the behavior is the same as always, and the name of the response as given to the driver is its path.
- When `alias` is provided
  1. it must be a string that will be both the name by which the response is keyed internally, and the name which is given to the driver for the response.
  2. the path to the response must be stored as metadata in the dictionary of responses, since we can no longer assume that the key is the path.
- **The alias to a constraint only pertains to the driver, it is not an addressable variable for use with `set_val` or `get_val`.**
- Currently, if the user adds a second response to the same variable, an error is raised.  The error will now inform the user that it can be avoided by providing an alias for the given constraint/objective.
- OpenMDAO should resolve the indices during the setup process and ensure that multiple constraints do not apply to the same indices of a variable.

## Example

The following code is currently invalid.  It assumes an output of size 3 where indices 0 and 1 are subject to equality constraints and index 2 is subject to an inequality constraint.

```
p.model.add_constraint('G.foo', indices=[0, 2], equals=0)
p.model.add_constraint('G.foo', indices=[1], lower=0, upper=100)
```

Following the implementation of this change, this should raise the following ValueError:

```
A constraint already exists on 'G.foo'.  Please provide an alias for any additional constraints, and ensure the constraints do not contain overlapping indices.
```

One valid way to alias would be

```
p.model.add_constraint('G.foo', indices=[0, 2], equals=0)
p.model.add_constraint('G.foo', indices=[1], lower=0, upper=100, alias='G[1]')
```

Or, aliasing both constraints:

```
p.model.add_constraint('G.foo', indices=[0, 2], equals=0, alias='G_endpoints)
p.model.add_constraint('G.foo', indices=[1], lower=0, upper=100, alias='G_midpoint')
```
