import numpy as np
import openmdao.api as om
import unittest


class TestCase1(unittest.TestCase):

    def test_broadcast_scalar_connection(self):
        """
        OpenMDAO should allow promotion to an input that appears to have a certain shape.
        Users should be allowed to connect an arbitrary variable with compatible src_indices to that input.
        """
        p = om.Problem()

        g1 = om.Group()

        # c1 contains scalar calculations
        ivc = om.IndepVarComp()
        ivc.add_output('y', val=5.0*np.ones(4,))
        ivc.add_output('x', val=np.linspace(0.0, 3.0, 4))
        p.model.add_subsystem('ivc', ivc)

        # c2 is vectorized calculations
        c2 = om.ExecComp('z = a * y',
                         z={'shape': (4,)},
                         y={'shape': (4,)},
                         a={'shape': (4,)})

        p.model.add_subsystem('g1', g1)
        g1.add_subsystem('g1', c2)

        # The ultimate source of a and y may be scalar, or have some other arbitrary shape
        g1.promotes('g1', inputs=['a', 'y'], src_indices=[0, 0, 0, 0], src_shape=(1,))

        p.model.connect('ivc.y', 'g1.y')

        # Now connect only a portion of some other output to a, which appears as a scalar input
        # (This currently breaks because we're specifying the src_indices of an input twice.)
        p.model.connect('ivc.x', 'g1.a', src_indices=[-1])

        p.setup()

        p.run_model()

        om.n2(p.model)