POEM ID:  055  
Title:  Min/Max Variable Print Option for Arrays  
authors: @andrewellis55(Andrew Ellis)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: N/A

Status:

- [x] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [ ] Integrated

## Motivation
When printing various debugging data, be in from the debug print or from 
Problem.list_problem_vars(), we only have two options for arrays - Printing 
the magnitude or printing the entire array. However when dealing 
very large arrays with widely varying values, neither of these options provide 
a great quick visual reference of how the array is interacting with upper and 
lower bounds of a constraint. For this reason it is propsed that an additional 
option be given to print the min and max of a given array as this gives a better 
reference with repespect to upper and lower bounds.

## Problem Statement
It is propsed that an additional option be given to Problem.list_problem_vars() 
and possibly also the debug_print of the driver to print the min and max of a 
given array as this gives a better reference with repespect to upper and lower 
bounds.

## Example to illustratre where this becomes useful
Suppose we are constraining the stress of a component for a series of 
100 load cases, neither printing the array nor showing the magnitude gives 
a quick visual check as to whether the constraint is satisfied 

```python
import openmdao.api as om 
import numpy as np

np.random.seed(42)
num_loads = 100

class Stress(om.ExplicitComponent):

    def setup(self):
        self.add_input('radius', units='mm')
        self.add_input('forces', shape=(num_loads), units='kN')

        self.add_output('area', units='mm**2')
        self.add_output('stress', shape=(num_loads,), units='MPa')

    def compute(self, inputs, outputs):
        outputs['area'] = 3.14159 * inputs['radius']**2
        outputs['stress'] = inputs['forces'] / outputs['area']

prob = om.Problem()
model = prob.model

model.add_subsystem('stress', Stress(), promotes=['*'])
model.add_design_var('radius', lower=0)
model.add_constraint('stress', upper=10)
model.add_objective('area')

prob.setup()
prob.set_val('forces', (np.random.rand(num_loads)**3), units='MN')

prob.driver = om.ScipyOptimizeDriver()
model.approx_totals()

prob.run_driver()

prob.list_problem_vars(
    cons_opts=['lower', 'upper'],
    print_arrays=True
)

```

## Implentation 
It can be up for discussion about what looks nicest and how to include this
in the API however my first crack at a general implementation is just a 
quick modification to `Problem._write_var_info_table()`. Note that I'm just 
replacing the existing array magnitude style here but I think that have the 
option to switch between both would be best.

I addtionally think something similar could be nice in the debug print, but 
that would require more digging into the drivers than I've done at this stage.

```python
    def _write_var_info_table(self, header, col_names, meta, vals, print_arrays=False,
                              show_promoted_name=True, col_spacing=1):
        """
        Write a table of information for the problem variable in meta and vals.

        Parameters
        ----------
        header : str
            The header line for the table.
        col_names : list of str
            List of column labels.
        meta : OrderedDict
            Dictionary of metadata for each problem variable.
        vals : OrderedDict
            Dictionary of values for each problem variable.
        print_arrays : bool, optional
            When False, in the columnar display, just display norm of any ndarrays with size > 1.
            The norm is surrounded by vertical bars to indicate that it is a norm.
            When True, also display full values of the ndarray below the row. Format is affected
            by the values set with numpy.set_printoptions
            Default is False.
        show_promoted_name : bool
            If True, then show the promoted names of the variables.
        col_spacing : int
            Number of spaces between columns in the table.
        """
        abs2prom = self.model._var_abs2prom

        # Get the values for all the elements in the tables
        rows = []
        for name, meta in meta.items():

            row = {}
            for col_name in col_names:
                if col_name == 'name':
                    if show_promoted_name:
                        row[col_name] = name
                    else:
                        if name in abs2prom['input']:
                            row[col_name] = abs2prom['input'][name]
                        elif name in abs2prom['output']:
                            row[col_name] = abs2prom['output'][name]
                        else:
                            # Promoted auto_ivc name. Keep it promoted
                            row[col_name] = name

                elif col_name == 'value':
                    row[col_name] = vals[name]
                else:
                    row[col_name] = meta[col_name]
            rows.append(row)

        col_space = ' ' * col_spacing
        print("-" * len(header))
        print(header)
        print("-" * len(header))

        # loop through the rows finding the max widths
        max_width = {}
        for col_name in col_names:
            max_width[col_name] = len(col_name)
        for row in rows:
            for col_name in col_names:
                cell = row[col_name]
                if isinstance(cell, np.ndarray) and cell.size > 1:
                    # out = '|{}|'.format(str(np.linalg.norm(cell)))  # Removed
                    out = str(np.array([min(cell), max(cell)]))       # Added
                else:
                    out = str(cell)
                max_width[col_name] = max(len(out), max_width[col_name])

        # print col headers
        header_div = ''
        header_col_names = ''
        for col_name in col_names:
            header_div += '-' * max_width[col_name] + col_space
            header_col_names += pad_name(col_name, max_width[col_name], quotes=False) + col_space
        print(header_col_names)
        print(header_div[:-1])

        # print rows with var info
        for row in rows:
            have_array_values = []  # keep track of which values are arrays
            row_string = ''
            for col_name in col_names:
                cell = row[col_name]
                if isinstance(cell, np.ndarray) and cell.size > 1:
                    # out = '|{}|'.format(str(np.linalg.norm(cell)))  # Removed
                    out = str(np.array([min(cell), max(cell)]))       # Added
                    have_array_values.append(col_name)
                else:
                    out = str(cell)
                row_string += pad_name(out, max_width[col_name], quotes=False) + col_space
            print(row_string)

            if print_arrays:
                left_column_width = max_width['name']
                for col_name in have_array_values:
                    print("{}{}:".format((left_column_width + col_spacing) * ' ', col_name))
                    cell = row[col_name]
                    out_str = pprint.pformat(cell)
                    indented_lines = [(left_column_width + col_spacing) * ' ' +
                                      s for s in out_str.splitlines()]
                    print('\n'.join(indented_lines) + '\n')

        print()
```

With the above implementation, the output of the example code is presented bellow. As can be
seen, it it now more visable that the stress constraint is interacting with the upper bound

```
Optimization terminated successfully    (Exit mode 0)
            Current function value: [96.11744123]
            Iterations: 10
            Function evaluations: 13
            Gradient evaluations: 10
Optimization Complete
-----------------------------------
----------------
Design Variables
----------------
name    value         size
------  ------------  ----
radius  [5.53128897]  1

-----------
Constraints
-----------
name           value                            size  lower   upper
-------------  -------------------------------  ----  ------  -----
stress.stress  [1.75192149e-06 1.00000000e+01]  100   -1e+30  10.0
               value:
               array([5.46629205e-01, 8.94021343e+00, 4.08056462e+00, 2.23221090e+00,
                      3.95118411e-02, 3.94935186e-02, 2.03872501e-03, 6.76108595e+00,
                      2.25980269e+00, 3.69344066e+00, 9.07441016e-05, 9.49274712e+00,
                      6.00151304e+00, 9.96065233e-02, 6.25400686e-02, 6.41841555e-02,
                      2.92992391e-01, 1.50338811e+00, 8.38461661e-01, 2.56981751e-01,
                      2.38308129e+00, 2.82398952e-02, 2.59412922e-01, 5.11597608e-01,
                      9.86943454e-01, 5.03615147e+00, 8.28249023e-02, 1.41475512e+00,
                      2.16309199e+00, 1.04271718e-03, 2.33309721e+00, 5.15887825e-02,
                      2.86399073e-03, 8.88872113e+00, 9.36769607e+00, 5.49632544e+00,
                      2.94067067e-01, 9.69414613e-03, 3.33280495e+00, 8.87170923e-01,
                      1.89097397e-02, 1.26321989e+00, 4.23095394e-04, 7.82255464e+00,
                      1.80297553e-01, 3.02551473e+00, 3.15104425e-01, 1.46345121e+00,
                      1.70008063e+00, 6.57184887e-02, 9.48320117e+00, 4.84536148e+00,
                      8.62753410e+00, 7.45444902e+00, 2.22373695e+00, 8.15103637e+00,
                      7.20970048e-03, 7.83162869e-02, 9.62497179e-04, 3.58237845e-01,
                      6.10893207e-01, 2.07865602e-01, 5.92173251e+00, 4.72391304e-01,
                      2.30681662e-01, 1.66290661e+00, 2.91175456e-02, 5.37082335e+00,
                      4.31074161e-03, 1.00000000e+01, 4.79140327e+00, 8.16383504e-02,
                      1.75192149e-06, 5.64167508e+00, 3.67445660e+00, 4.03081805e+00,
                      4.77328869e+00, 4.22356209e-03, 4.79226386e-01, 1.61845357e-02,
                      6.68938698e+00, 2.51933120e+00, 3.76947028e-01, 2.67125684e-03,
                      3.12899525e-01, 3.57752428e-01, 4.04076234e+00, 2.69622305e+00,
                      7.26576106e+00, 1.09551147e+00, 1.77962564e-02, 3.77497099e+00,
                      4.58124699e+00, 1.83962794e+00, 4.76766213e+00, 1.25267796e+00,
                      1.48606268e+00, 8.13076036e-01, 1.70875453e-04, 1.30664801e-02])


----------
Objectives
----------
name         value          size
-----------  -------------  ----
stress.area  [96.11744123]  1
```

## Pull Requests
To be created if this general concept seems acceptable

