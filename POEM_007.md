POEM ID:  007  
Title:   String Compatibility for ExternalCodeComp and ExternalCodeImplicitComp Command Options  
authors: [DKilkenny] (Danny Kilkenny)    
Competing POEMs: [N/A]  
Related POEMs: [N/A]  
Associated Implementation PR:    

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated


Motivation
----------

Feedback from the community has indicated that users want to pass additional arguments to their external code. One example of this can be seen on this [Stack Overflow post](https://stackoverflow.com/questions/59187224/running-matlab-scripts-as-externalcode-component). The current implementation can be confusing when adding flag arguments in their list.


Description
-----------

This POEM proposes changing `ExternalCodeComp` and `ExternalCodeImplicitComp` to allow the user to pass a string or list to `command`, `command_apply`, and `command_solve`. This will be a backward compatible change. The current implementation only allows for a list of arguments which creates difficulties when a user wants to pass flags within that list.

Example
-------

Using a current example from `ExternalCodeImplicitComp`, we will show a modification to demonstrate the new API.

To run the example, this code should be copy/pasted into a file that is named `extcode_paraboloid.py`.
```
if __name__ == '__main__':
    import sys

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    with open(input_filename, 'r') as input_file:
        file_contents = input_file.readlines()

    x, y = [float(f) for f in file_contents]

    f_xy = (x-3.0)**2 + x*y + (y+4.0)**2 - 3.0

    with open(output_filename, 'w') as output_file:
        output_file.write('%.16f\n' % f_xy)
```

In a seperate file, paste the code below and run the file. Inside the code we changed `self.options['command']` from a list of arguments to a string.
```
import openmdao.api as om
import sys

class ParaboloidExternalCodeComp(om.ExternalCodeComp):
    def setup(self):
        self.add_input('x', val=0.0)
        self.add_input('y', val=0.0)

        self.add_output('f_xy', val=0.0)

        self.input_file = 'paraboloid_input.dat'
        self.output_file = 'paraboloid_output.dat'

        # providing these is optional; the component will verify that any input
        # files exist before execution and that the output files exist after.
        self.options['external_input_files'] = [self.input_file]
        self.options['external_output_files'] = [self.output_file]

        # Both self.option['command'] examples below will work but here we demonstrate the new functionality
        # String implementation
        self.options['command'] = 'python extcode_paraboloid.py paraboloid_input.dat paraboloid_output.dat'

        # List implementation
        # self.options['command'] = [
        #     sys.executable, 'extcode_paraboloid.py', self.input_file, self.output_file
        # ]

    def compute(self, inputs, outputs):
        x = inputs['x']
        y = inputs['y']

        # generate the input file for the paraboloid external code
        with open(self.input_file, 'w') as input_file:
            input_file.write('%.16f\n%.16f\n' % (x, y))

        # the parent compute function actually runs the external code
        super(ParaboloidExternalCodeComp, self).compute(inputs, outputs)

        # parse the output file from the external code and set the value of f_xy
        with open(self.output_file, 'r') as output_file:
            f_xy = float(output_file.read())

        outputs['f_xy'] = f_xy


prob = om.Problem()
model = prob.model

# create and connect inputs
model.add_subsystem('p1', om.IndepVarComp('x', 3.0))
model.add_subsystem('p2', om.IndepVarComp('y', -4.0))
model.add_subsystem('p', om.ParaboloidExternalCodeComp())

model.connect('p1.x', 'p.x')
model.connect('p2.y', 'p.y')

# run the ExternalCodeComp Component
prob.setup()
prob.run_model()

# print the output
print(prob['p.f_xy'])

# Expected output is: 15
```

References
---------

1. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/external_code_comp.html
2. http://openmdao.org/twodocs/versions/2.9.1/features/building_blocks/components/external_code_implicit_comp.html
