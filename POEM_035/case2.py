import numpy as np
import openmdao.api as om
import unittest


class TestCase2(unittest.TestCase):

    def test_multiple_inputs_different_src_indices(self):
        """
        When different variables get promoted to the same name, but have different src_indices, this
        should be supported as long as the src_shape of the different promotions is compatible or
        made so by the set_input_defaults call.
        """
        p = om.Problem()

        g1 = om.Group()
        g2 = om.Group()

        # c1 contains scalar calculations
        c1 = om.ExecComp('y = a0 + b',
                         y={'shape': (1,)},
                         a0={'shape': (1,)},
                         b={'shape': (1,)})

        # c2 is vectorized calculations
        c2 = om.ExecComp('z = a * y',
                         z={'shape': (4,)},
                         y={'shape': (4,)},
                         a={'shape': (4,)})

        p.model.add_subsystem('g1', g1, promotes_inputs=['a', 'b'])
        g1.add_subsystem('c1', c1, promotes_inputs=[('a0', 'a'), 'b'], promotes_outputs=['y'])
        g2.add_subsystem('c2', c2, promotes_inputs=['a', 'y'])
        g1.add_subsystem('g2', g2)

        g1.promotes('g2', inputs=['y'], src_indices=[0, 0, 0, 0], src_shape=(1,))
        g1.promotes('g2', inputs=['a'], src_indices=[0, 0, 0, 0], src_shape=(1,))
        p.model.promotes('g1', inputs=['a'], src_indices=[0], src_shape=(1,))

        p.setup()

        p.run_model()

        om.n2(p.model)
