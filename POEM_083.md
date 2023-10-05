POEM ID: 083  
Title: Specifying order when adding a subsystem  
authors: robfalck (Rob Falck)  
Competing POEMs:  
Related POEMs:  N/A  
Associated implementation PR: N/A

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted 
- [x] Rejected
- [ ] Integrated

## Motivation

Adding subsystems to a Group in OpenMDAO currently places the subsystem at the end.
In situations where users may want to insert a subsystem into the middle of the sequence, they're required to alter the ordering after the fact.
It would be simpler if they had the option to specify the insertion point when adding the subsystem.

## Proposed Solution

`Group.add_subsystem` will support two new arguments: `before` and `after`.

When both of these are `None` (the default) the systems will be placed at the end of the current list, which is the current behavior.

These values can be specified with either strings (the name of the preceeding or following system), or with integers (the index of the preceeding or following system.)

**These values take effect immediately, not during setup.**

For instance, adding system 'a' to the beginning of the list and then system 'b' to the beginning of the list will result in system 'b' being first, followed by system 'a'.
In addition, if the name specified in `before` or `after` is not present in the subsystems at the time `add_subsystem` is called, it will result in an error.

## Example

### Insert a new system Foo as the first component in a group.
```
g.add_subsystem('foo', FooComp(), before=0)
```

### Add a new system Foo as the last component in a group (current behavior)

```
g.add_subsystem('foo', FooComp())
```

or equivalently

```
g.add_subsystem('foo', FooComp(), after=-1)
```

### Add a new system Foo before a system named 'bar'

```
g.add_subsystem('foo', FooComp(), before='bar')
```
