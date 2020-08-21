POEM ID: 005  
Title: An OpenMDAO Plugin System  
authors: [naylor-b]  
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


To provide a way for users outside of the OpenMDAO dev team to contribute code that is
easily discoverable and installable without requiring that it be added to the OpenMDAO repository.


# Description

Creating a plugin that is fully integrated into the OpenMDAO framework will require the following:

1. The plugin will be part of an installable python package.
2. An entry point will be added to the appropriate entry point group (see below) of the
    *entry_points* argument passed to the *setup* call in the *setup.py* file for the
    python package containing the plugin.
3. The same entry point group string mentioned above will be added to the *keywords* arg passed
    to the *setup* call in the *setup.py* file for the python package containing the plugin.


## Entry Point Groups

The following table shows the entry point groups that OpenMDAO recognizes.


Entry Point Group         | Type              | Entry Point Refers To
:------------------------ | :---------------- | :--------------------
openmdao_component        | Component         | class or factory funct
openmdao_group            | Group             | class or factory funct
openmdao_driver           | Driver            | class or factory funct
openmdao_lin_solver       | LinearSolver      | class or factory funct
openmdao_nl_solver        | NonlinearSolver   | class or factory funct
openmdao_surrogate_model  | SurrogateModel    | class or factory funct
openmdao_case_recorder    | CaseRecorder      | class or factory funct
openmdao_case_reader      | BaseCaseReader    | funct returning (file_extension, class or factor funct)
openmdao_command          | command line tool | funct returning (setup_parser_func, exec_func, help_string)


## Discovery of Plugins

### Discovery of Installed Plugins

A new command line tool will be added to OpenMDAO to allow a user to discover plugins that
have been installed in the user's python environment.  This command, `openmdao list_installed`,
will list all entry points belonging to specified entry point groups.  For example, the command
`openmdao list_installed components` will list all entry points in the `openmdao_component`
entry point group, producing output like the following:

Installed components:

  Package: openmdao  Version: 2.9.1 

    Class or Function                 Module  
    -----------------                 ------  
    AddSubtractComp                   openmdao.components.add_subtract_comp
    AkimaSplineComp                   openmdao.components.akima_spline_comp
    BalanceComp                       openmdao.components.balance_comp
    BsplinesComp                      openmdao.components.bsplines_comp
    CrossProductComp                  openmdao.components.cross_product_comp
    DemuxComp                         openmdao.components.demux_comp
    DotProductComp                    openmdao.components.dot_product_comp
    EQConstraintComp                  openmdao.components.eq_constraint_comp
    ExecComp                          openmdao.components.exec_comp
    ExternalCodeComp                  openmdao.components.external_code_comp
    ExternalCodeImplicitComp          openmdao.components.external_code_comp
    KSComp                            openmdao.components.ks_comp
    LinearSystemComp                  openmdao.components.linear_system_comp
    MatrixVectorProductComp           openmdao.components.matrix_vector_product_comp
    MetaModelStructuredComp           openmdao.components.meta_model_structured_comp
    MetaModelUnStructuredComp         openmdao.components.meta_model_unstructured_comp
    MultiFiMetaModelUnStructuredComp  openmdao.components.multifi_meta_model_unstructured_comp
    MuxComp                           openmdao.components.mux_comp
    VectorMagnitudeComp               openmdao.components.vector_magnitude_comp
    IndepVarComp                      openmdao.core.indepvarcomp

  Package: my_plugins_package  Version: 0.1 

    Class or Function                 Module  
    -----------------                 ------  
    MyComponent                       my_plugins_package.my_comp_plugin



Note that there is only one actual plugin, `MyComponent`, in the entry points listed above.  
The others are built-in components that are part of the OpenMDAO framework.  Also, the 
`openmdao list_installed` command line tool will have include `(-i)` and exclude `(-x)` options 
to allow filtering of packages to control what is displayed.  For example, to show only component plugins
and hide all of the 'built-in' openmdao components, you could do 
`openmdao list_installed components -x openmdao`.
Docstrings for the entry point targets can be displayed using the `-d` arg, for example:
`openmdao list_installed components -d`.


### Discovery of Plugins Available on PyPI

The PyPI web API will be used to search for packages available on PyPI that have included
`openmdao` and/or one or more of the openmdao entry point group names in their `keywords`.


### Discovery of Plugins on GitHub

To make a github repository containing OpenMDAO plugins easily discoverable by users, the
appropriate openmdao entry point group name(s) should be added as *topics* to the repository
after converting any underscores (`_`) to hyphens (`-`).  This is necessary because underscores
are illegal in github topic names and hyphens are illegal in entry point group names.
Adding such a topic to a github repository will make that repository show up when someone
searches github using the hyphenated entry point group name.


# Implementation Details


## Types of Entry Points


### 'Typical' entry points


Most types of entry points are handled in exactly the same way.  The entry point merely refers
to the class definition of the plugin or to some factory function that returns an instance of
the plugin.  The following entry point types are all handled in this way:

* component
* group
* driver
* nl_solver
* lin_solver
* surrogate_model
* case_recorder


Here's an example of how to specify the *entry_points* arg to the *setup* call in `setup.py`
for a component plugin class called `MyComponent` in a package called `my_plugins_package`
in a module called `my_comp_plugin.py`:

```python
entry_points={
    'openmdao_component': [
        'mycompplugin=my_plugins_package.my_comp_plugin:MyComponent'
    ]
}
```

The actual name of the entry point, `mycompplugin` in this case, is not used for anything
in a 'typical' entry point.  Also, note that all of the types listed above will function perfectly 
well in OpenMDAO without defining any entry points.  The entire purpose of the entry points in this
case is to allow the user to discover all of the components/groups/etc that have been
installed in the current python environment using the `openmdao list_installed` command.


### Entry Points in openmdao_case_reader


The entry point for a case reader should point to a function that returns a tuple of the form
(file_extension, class), where *file_extension* contains the leading dot, for example '.sql',
and *class* could either be the class definition of the plugin or a factory function returning
an instance of the plugin.  The file extension is used to provide an automatic mapping to the
correct case reader based on the file extension of the file being read.


### Entry Points in openmdao_command


An entry point for an OpenMDAO command line tool plugin should point to a function that returns
a tuple of the form (setup_parser_func, exec_func, help_string).  For example:

```python
def _hello_setup():
    """
    This command prints a hello message after final setup.
    """
    return (_hello_setup_parser, _hello_exec, 'Print hello message after final setup.')
```

The *setup_parser_func* is a function taking a single *parser* argument that adds any arguments
expected by the plugin to the *parser* object.  The *parser* is an *argparse.ArgumentParser* object.
For example, the following code sets up a subparser for a `openmdao hello` command that adds a file 
argument and a `--repeat` option:


```python
def _hello_setup_parser(parser):
    """
    Set up the openmdao subparser (using argparse) for the 'openmdao hello' command.

    Parameters
    ----------
    parser : argparse subparser
        The parser we're adding options to.
    """
    parser.add_argument('-r', '--repeat', action='store', dest='repeats',
                        default=1, type=int, help='Number of times to say hello.')
    parser.add_argument('file', metavar='file', nargs=1,
                        help='Script to execute.')
```


The *exec_func* is a function that performs whatever action is necessary for the command line
tool plugin to operate.  Typically this will involve registering another function that is to
execute at some point during the execution of a script file.  For example, the following
function registers a function that prints a `hello` message, specifying that it should execute
after the `Problem._final_setup` method.


```python
def _hello_exec(options, user_args):
    """
    This registers the hook function and executes the user script.

    Parameters
    ----------
    options : argparse Namespace
        Command line options.
    user_args : list of str
        Args to be passed to the user script.
    """
    script = options.file[0]

    def _hello_after_final_setup(prob):
        for i in range(options.repeats):
            print("Hello after final_setup in script {}!".format(os.path.basename(script)))

    # register the hook to execute after Problem.final_setup
    _register_hook('final_setup', class_name='Problem', post=_hello_after_final_setup)

    # load and execute the given script as __main__
    _load_and_exec(script, user_args)
```

The final entry in the tuple returned by the function referred to by the entry point 
(in this case *_hello_setup*)
is a string containing a high level description of the command.  This description will be displayed
along with the name of the command when a user runs `openmdao -h`.

Here's an example of how to specify the *entry_points* arg to the *setup* call in `setup.py`
for our command line tool described above if it were inside of a package called `my_plugins_package`
in a file called `hello_cmd.py`:


```python
entry_points={
        'openmdao_command': [
            'hello=my_plugins_package.hello_cmd:_hello_setup'
        ]
}
```

In this case, the name of our entry point, `hello`, will be the name of the openmdao command line
tool, so the user will activate the tool by typing `openmdao hello`.


