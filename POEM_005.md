POEM ID: 005  
Title: An OpenMDAO Plugin System  
authors: [naylor-b]  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR:  

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated



# Motivation


To provide a way for users outside of the OpenMDAO dev team to contribute code that is
easily discoverable and installable without requiring that it be added to the OpenMDAO repository.


# Description


Creating a plugin that is fully integrated into the OpenMDAO framework will require the following:

    1. An entry point will be added to the appropriate entry point group (see below) of the
       *entry_points* argument passed to the *setup* call in the *setup.py* file for the
       python package containing the plugin.
    2. The same entry point group string mentioned above will be added to the *keywords* arg passed
       to the *setup* call in the *setup.py* file for the python package containing the plugin.



Entry Point Group       | Type              | Entry Point Refers To
----------------------- | ----------------- | ---------------------
openmdao_components     | Component         | class or factory funct
openmdao_groups         | Group             | class or factory funct
openmdao_drivers        | Driver            | class or factory funct
openmdao_lin_solvers    | LinearSolver      | class or factory funct
openmdao_nl_solvers     | NonlinearSolver   | class or factory funct
openmdao_case_recorders | CaseRecorder      | class or factory funct
openmdao_case_readers   | BaseCaseReader    | funct returning (file_extension, class)
openmdao_commands       | command line tool | funct returning (setup_parser_func, exec_func, help_string)


## Types of Entry Points


### 'typical' entry points


Most types of entry points are handled in exactly the same way.  The entry point merely refers
to the class definition of the plugin or to some factory function that returns an instance of
the plugin.  The following entry point types are all handled in this way:

* components
* groups
* drivers
* nl_solvers
* lin_solvers
* case_recorders


Here's an example of how to specify the *entry_points* arg to the *setup* call in `setup.py`
for a component plugin class called `MyComponent` in a package called `my_plugins_package`
in a module called `my_comp_plugin.py`:

```python
entry_points={
    'openmdao_components': [
        'mycompplugin=my_plugins_package.my_comp_plugin:MyComponent'
    ]
}
```

Note that the actual name of the entry point, `mycompplugin`, is not used for anything in a
'typical' entry point.


### case_readers


The entry point for a case reader should point to a function that returns a tuple of the form
(file_extension, class), where *file_extension* contains the leading dot, for example '.sql',
and *class* could either be the class definition of the plugin or a factory function returning
an instance of the plugin.  The file extension is used to provide an automatic mapping to the
correct case reader based on the file extension of the file being read.


### commands


An entry point for an OpenMDAO command line tool plugin should point to a function that returns
a tuple of the form (setup_parser_func, exec_func, help_string).  For example:

```python
def _hello_setup():
    """
    This is registered as an 'openmdao_commands' entry point.

    It should return a tuple of the form (setup_parser_func, exec_func, help_string).
    """
    return (_hello_setup_parser, _hello_exec, 'Print hello message after final setup.')
```

The *setup_parser_func* is a function taking a single *parser* argument that adds any arguments
expected by the plugin to the *parser* object.  For example, the following code sets up a
subparser for a `openmdao hello` command:


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

The final entry in the tuple returned by function referred to by the entry point (in this case *_hello_setup*)
is a string containing a high level description of the command.  This description will be displayed
along with the name of the command when a user runs `openmdao -h`.

Here's an example of how to specify the *entry_points* arg to the *setup* call in `setup.py`
for our command line tool described above if it were inside of a package called `my_plugins_package`
in a file called `hello_cmd.py`:


```python
entry_points={
        'openmdao_commands': [
            'hello=my_plugins_package.hello_cmd:_hello_setup'
        ]
}
```

In this case, the name of our entry point, `hello`, will be the name of the openmdao command line
tool, so the user will activate the tool by typing `openmdao hello`.


