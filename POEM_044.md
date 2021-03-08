POEM ID: 044  
Title: Global User Preferences  
authors: [robfalck]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated


Motivation
----------
OpenMDAO currently has case-by-case settings for the verbosity of various warnings and other information.
Experienced users may wish to silence a lot of these warnings in most cases.
For this sort of behavior, it makes sense that a user may want to save their global preferences for use across cases.
This POEM proposes the addition of a user preferences file: ~/.openmdao.cfg


Config File Guidelines
----------------------

The following are some guidelines for the configuration file.

1. The default configuration options will be stored in the OpenMDAO repo and installed when OpenMDAO is installed.

We'll nominally call this file `/path_to_openmdao/openmdao.cfg`

2. A user-specific set of options will be stored in `~/.openmdao.cfg`

Values set in `~/.openmdao.cfg` will override values in `/path_to_openmdao/openmdao.cfg`

3. The .openmdao.cfg file will initially be used to store options pertaining to the verbosity of warnings.

The settings in the config should not affect results, although this may eventually change.

4. The OpenMDAO command line should have a `config` option to create the file or view its current values.

`openmdao config --create` will create a new default configuration file at ~/.openmdao.cfg

`openmdao config` will show the contents of the configuration file.

`openmdao config --diff` will show the difference between the user's settings and the defaults in the OpenMDAO directory.

5. To avoid the addition of dependencies, use the configparser module in the standard library for the file format.

6. Values stored in the config file will be _defaults_ that can be overridden in global openmdao options.

6. Proposed structure

```
[checks]
auto_ivc_warnings = yes
comp_has_no_outputs = yes
cycles = no
dup_inputs = yes
missing_recorders = yes
out_of_order = yes
promotions = no
solvers = yes
system = yes
unconnected_inputs = no

[component_warnings]
distributed_component_no_src_indices = warn

[connection_warnings]
unitless_to_units = warn

[optimizer_warnings]
singular_jac_behavior = warn

```

Checks will be set to enabled (1) be disabled (0)
Warnings will use the numpy seterr apporach for parsing warnings:

Warnings will simply warn when set to `warn`.
Disabling a warnings will be performed by setting it to `ignore`.
Warnings can be promoted to errors by setting them to `raise`.

Setting options in a script
---------------------------

A new nested dictionary will be added:  `openmdao.api.options`.

```
om.options['connection_warnings']['unitless_to_units'] = 'ignore'
om.options['optimizer_warnings']['singular_jac_behavior'] = 'raise'
```
