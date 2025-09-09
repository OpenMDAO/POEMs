POEM ID:  096  
Title:  Option to Minimize Constraint Violation  
authors: andrewellis55 (Andrew Ellis) and robfalck (Rob Falck)  
Competing POEMs: N/A  
Related POEMs: N/A  
Associated implementation PR: https://github.com/OpenMDAO/OpenMDAO/pull/3360 and https://github.com/OpenMDAO/OpenMDAO/pull/3593

Status:

- [ ] Active
- [ ] Requesting decision
- [ ] Accepted
- [ ] Rejected
- [x] Integrated

## Overview  
This POEM propose the addition of an option at the problem or driver level to alternatively minimize the sum of the constraint violation rather than the objective.

## Motivation  
There are three motivativing cases for the addition of this functionality.

**1. Finding root cause of misconfigured optimizations/checking if problem is feasible**  
Many optimization runs fail to converge. When the reason for this is an incorrect partial or poor scaling, there are many tools available to help debug this. In other instances where there are many user configuration options are avaialble, it is more common that the user may have simply select a configuration for which no feasible solution space exists. Some optimizers are better than others at alerting the user to this, however the standard optimizer that ships with OpenMDAO (scipy optimize SLSQP) does not communicate this very effectively.

Take the following example problem. There are two constraints that conflict with each other and one that is completely feasible.

```python
import openmdao.api as om

class Opt(om.ExplicitComponent):

    def setup(self):
        self.add_input('x1')
        self.add_design_var('x1')
        self.add_input('x2')
        self.add_design_var('x2')

        self.add_output('y')
        self.add_objective('y')

        self.add_output('infeasible_con1')
        self.add_constraint('infeasible_con1', lower=0)

        self.add_output('infeasible_con2')
        self.add_constraint('infeasible_con2', lower=0)

        self.add_output('feasible_con')
        self.add_constraint('feasible_con', lower=0)

    def compute(self, inputs, outputs):
        x1 = inputs['x1']
        x2 = inputs['x2']

        # Objective
        outputs['y'] = x1**2 + x2**2

        # Infeasible Constraint
        outputs['infeasible_con1'] = 2*x1 + 5
        outputs['infeasible_con1'] = -2*x1 - 5

        # Feasible Constriant
        outputs['feasible_con'] = x2 - 5

if __name__ == '__main__':
    prob = om.Problem()
    prob.model.add_subsystem('sys', Opt(), promotes=['*'])
    prob.setup()
    prob.driver = om.ScipyOptimizeDriver()
    prob.run_driver()
    prob.list_problem_vars(cons_opts=['lower', 'upper'])

```

```
Positive directional derivative for linesearch    (Exit mode 8)
            Current function value: 2.0
            Iterations: 5
            Function evaluations: 1
            Gradient evaluations: 1
Optimization FAILED.
Positive directional derivative for linesearch
-----------------------------------
----------------
Design Variables
----------------
name  val   size  
----  ----  ---- 
x1    [1.]  1
x2    [1.]  1

-----------
Constraints
-----------
name             val    size  lower  upper
---------------  -----  ----  -----  -----
infeasible_con1  [-7.]  1     0.0    1e+30
infeasible_con2  [1.]   1     0.0    1e+30
feasible_con     [-4.]  1     0.0    1e+30

----------
Objectives
----------
name  val   size
----  ----  ----
y     [2.]  1
```

We can see by looking at the results that despite `feasible_con` being feasible, the optimizer makes no attempt to bring it into the feasible region. If we imagine a problem with hundreds of constraints where one single constraint is infeasible, the user may look at a final output of a failed optimization with hundreds of constraint violations and have no guidance towards which is the single (or set of) infeasbile constraints.

Using the new functionality proposed in this POEM, following a failed opt of this manner, the user could run the minimization of constraint violation to check if the problem is feasible at all. Ideally this minimization would leave only the infeasible constraints violated. The user can then correct their configuration paramters to ensure the problem is feasible and then re-run objective minimization problem. A user could choose to run the feasibility checks could also be run prior to the objective minimization if desired.

**2. Finding a "good enough" point**  
In some engineering problems, a "good enough" solution is often acceptable. If a problem is infeasible, running a minimization of constraint violation can get a solution that is "as close to feasible as possible" which might be alright or at least worth looking at in some applications.

**3. Finding a feasible starting point**  
Although most modern optimizers can already deal with this problem, many optimizers do perform better if starting from a feasible starting point. Minimizing the sum of the constraint violation can help a user get to a feasible starting point before beginning the optimization. While many modern optimizers can account for infeasile starts, it could be a "nice to have" in the framework.

## Implementation

This behavior can be achieved by using `scipy.optimize.least_squares` to vary the design variables such that the L2 norm of the constraint violations is minimized.
Scipy's `least_squares` method observes bounds of design variables and allows for other norms to be minimized, such as a "soft_l1" approximation.

## Description
See https://github.com/OpenMDAO/OpenMDAO/pull/3360
See https://github.com/OpenMDAO/OpenMDAO/pull/3593



