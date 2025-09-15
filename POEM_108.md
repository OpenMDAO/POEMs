POEM ID: 108  
Title:  Using Pydantic for validation/serialization/deserialization  
authors: naylor-b (Bret Naylor)  
Competing POEMs: None  
Related POEMs:  None  
Associated implementation PR: N/A  

Status:  

- [x] Active  
- [ ] Requesting decision  
- [ ] Accepted  
- [ ] Rejected  
- [ ] Integrated  


## Motivation

Using a declarative input format to create an OpenMDAO model would be easier for many usrs than 
writing a python script.  Having such a format could also help to facilitate the development of
a GUI for building and editing OpenMDAO models.

## Description

This POEM will investigate the use of the Pydantic package to add validation, serialization, and
deserialization capability to OpenMDAO.  Pydantic provides all these capabilities, so the main
question is how well Pydantic can be integrated into OpenMDAO.  This POEM will also serve as a place
to document various implementation details so they won't be forgotten if we revisit this later.


## Pydantic

To use Pydantic, the first step is to declare a class for the data model that inherits from
Pydantic's BaseModel class.  Type information specified for class attributes
(called fields by Pydantic) is used for validation.  A field in a pydantic data model corresponds
to an option in an OptionsDictionary.

An input dict can be validated by a pydantic data model class by passing the dict to the
`model_validate` class method, which returns an instantiated data model.

A data model instance can be serialized to a dict by calling `model_dump` on it.  Calling
`model_dump_json` will serialize to a JSON-encoded string.


### OptionsDictionary Replacement

An OpenMDAO OptionsDictionary can be replaced with a Pydantic data model, with a few caveats:

- Fields in a pydantic data model must have valid python names, so fields containing characters like
':' would no longer be legal.

- Fields cannot be added to a data model dynamically.  They must be known when the data model class
is declared.

- Pydantic data models don't have a dict-like interface like OptionsDictionary does, but it was easy
enough to declare an OptionsBaseModel data model with __getitem__, __setitem__, etc., defined.

- Pydantic models by default do validation only on instantiation of a data model, not during assignment
to attributes of a data model instance. This won't work for OpenMDAO since we allow users to set options
at various times.  We activate on-assignment validation by setting 
`model_config = ConfigDict(validate_assignment=True)` in the data model.  In the Pydantic docs they
say this may impact performance.

- OpenMDAO's OptionsDictionary allows an option to be declared with a `values` arg, which specifies
a set of allowed values for that option.  To mimic that in Pydantic, you have to create an Enum 
class and use that as the type of the data model field, or a Union of Literals.

- Pydantic does allow for certain fields to be required to be set, but doesn't work well in OpenMDAO
because the check for the required field happens too early.  A workaround for that is to default the
value to None and explicitly check for a non-None value at some later point.



Here's an example of what the replacement for ExplicitComponent options looks like:

```python
class ExplicitComponentOptions(SystemOptions):
    distributed: bool = Field(default=False,
                             desc='If True, set all variables in this component as distributed '
                                  'across multiple processes')
    run_root_only: bool = Field(default=False,
                             desc='If True, call compute, compute_partials, linearize, '
                                  'apply_linear, apply_nonlinear, solve_linear, solve_nonlinear, '
                                  'and compute_jacvec_product only on rank 0 and broadcast the '
                                  'results to the other ranks.')
    always_opt: bool = Field(default=False,
                             desc='If True, force nonlinear operations on this component to be '
                                  'included in the optimization loop even if this component is not '
                                  'relevant to the design variables and responses.')
    use_jit: bool = Field(default=True,
                             desc='If True, attempt to use jit on compute_primal, assuming jax or '
                             'some other AD package capable of jitting is active.')
    default_shape: tuple = Field(default=(1,),
                             desc='Default shape for variables that do not set val to a non-scalar '
                             'value or set shape, shape_by_conn, copy_shape, or compute_shape.'
                             ' Default is (1,).')
```

Note that the class above inherits from SystemOptions.  Pydantic data models can inherit fields from
base classes and override them if needed.  However, they cannot delete base class fields, so we can't
`undeclare` options like we could with OptionsDictionary.


### OpenMDAO class vs. data model

Because pydantic uses a metaclass to do heavy manipulation of data model classes, I decided to keep
data models separate from OpenMDAO classes rather then having OpenMDAO classes inherit from BaseModel.
Instead, a registry is maintained in the `DataModelManager` class that maps an OpenMDAO class to its 
corresponding data model.  This means we have to have functions to update the OpenMDAO class based 
on its data model and vice versa.  The `DataModelManager.register` class decorator is used to bind a 
data model to a corresponding OpenMDAO class.  For example, the data model for an OpenMDAO Group is 
shown below:

```python
@DataModelManager.register(Group)
class GroupModel(SystemModel):
    options: GroupOptions = Field(default_factory=GroupOptions)
    connections: List[ConnectionData] = Field(default_factory=list)
    subsystems: List[PolymorphicModel] = Field(default_factory=list)
    input_defaults: List[InputDefaultData] = Field(default_factory=list)
    linear_solver: LinearSolverModel = Field(default_factory=LinearSolverModel)
    nonlinear_solver: NonlinearSolverModel = Field(default_factory=NonlinearSolverModel)
```

### Deserialization

In order to be able to create an OpenMDAO model based on the contents of a dict (which was created
from a json or yaml string), there has to be some kind of declaration in the dict that tells python
which class to instantiate.  This was done by having a 'type' field in our data classes that 
specifies the full module path name of a class.  A `TypeBaseModel` data model class was created 
that contained this 'type' field, along with optional 'args' and 'kwargs'.  These three fields provide all
of the information necessary to instantiate a class.  Any OpenMDAO data model classes needing this
runtime class lookup functionality are inherited from `TypeBaseModel`.

Any `TypeBaseModel` subclass will look similar to the following in dict form:

```python
    {
        'type': 'openmdao.test_suite.components.sellar.SellarDis1',
        'name': 'd1',
        # 'args': [...]   # args are not typically needed but are supported
        # 'kwargs': {...}  # kwargs are not typically needed but are supported

        # put other fields here...
    }
```

### Example

An example of a simple Sellar model declared as a dict follows:

```python
from openmdao.utils.validation import DataModelManager as dmm

cfg = {
    'type': 'openmdao.core.problem.Problem',
    'name': 'Sellar_MDA',

    'driver': {
        'type': 'openmdao.drivers.scipy_optimizer.ScipyOptimizeDriver',
        'options': {
            'invalid_desvar_behavior': 'warn',
            'optimizer': 'SLSQP',
            'tol': 1.0e-8
        }
    },
    'model': {
        'type': 'openmdao.core.group.Group',
        'subsystems': [
            {
                'type': 'openmdao.core.group.Group',
                'name': 'cycle',
                'subsystems': [
                    {
                        'type': 'openmdao.test_suite.components.sellar.SellarDis1',
                        'name': 'd1',
                        'promotes_inputs': ['x', 'z', 'y2'],
                        'promotes_outputs': ['y1']
                    },
                    {
                        'type': 'openmdao.test_suite.components.sellar.SellarDis2',
                        'name': 'd2',
                        'promotes_inputs': ['z', 'y1'],
                        'promotes_outputs': ['y2']
                    }
                ],
                'input_defaults': [
                    {
                        'name': 'z',
                        'src_shape': (2,)
                    }
                ],
                'nonlinear_solver': {
                    'type': 'openmdao.solvers.nonlinear.nonlinear_block_gs.NonlinearBlockGS'
                },
                'promotes_inputs': ['x', 'z']
            },
            {
                'type': 'openmdao.components.exec_comp.ExecComp',
                'name': 'obj_cmp',
                'exprs': 'obj = x**2 + z[1] + y1 + exp(-y2)',
                'promotes': ['x', 'z', 'y1', 'y2', 'obj']
            },
            {
                'type': 'openmdao.components.exec_comp.ExecComp',
                'name': 'con_cmp1',
                'exprs': 'con1 = 3.16 - y1',
                'promotes': ['con1', 'y1']
            },
            {
                'type': 'openmdao.components.exec_comp.ExecComp',
                'name': 'con_cmp2',
                'exprs': 'con2 = y2 - 24.0',
                'promotes': ['con2', 'y2']
            }
        ],
        'design_variables': [
            {
                'name': 'x',
                'lower': -1.0,
                'upper': 10.0
            },
            {
                'name': 'z',
                'lower': -1.0,
                'upper': 10.0
            }
        ],
        'objectives': [
            {
                'name': 'obj_cmp.obj',
            }
        ],
        'constraints': [
            {
                'name': 'con_cmp1.con1',
                'upper': 0.0
            },
            {
                'name': 'con_cmp2.con2',
                'upper': 0.0
            }
        ],
    },
}

prob = dmm.from_dict(cfg)
prob.model.approx_totals()
prob.setup()
prob.set_val('x', 2.0)
prob.set_val('z', [0.0, 0.0])
prob.set_solver_print(level=0)
prob.run_model()

```
