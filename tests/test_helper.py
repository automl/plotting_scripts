import unittest

import numpy as np
from plottingscripts.utils import helper


class helperTest(unittest.TestCase):

    def test_bootstrap_sample_idx(self):
        # Should not do anything
        resample_i = helper.bootstrap_sample_idx(num_samples=1,
                                                 boot_strap_size=10)
        self.assertListEqual(list(resample_i), [0]*10)

        resample_i = helper.bootstrap_sample_idx(num_samples=2,
                                                 boot_strap_size=1000)
        self.assertEqual(np.int(np.sum(resample_i)/1000*10), 5)

        # Test random seeds
        np.random.seed(1)
        a = np.random.get_state()
        np.random.seed(50)
        resample_i = helper.bootstrap_sample_idx(num_samples=50,
                                                 boot_strap_size=10, rng=a)
        self.assertListEqual(list(resample_i),
                             [20, 36, 0, 15, 7, 4, 9, 17, 19, 26])

        resample_i = helper.bootstrap_sample_idx(num_samples=50,
                                                 boot_strap_size=10, rng=1)
        self.assertListEqual(list(resample_i),
                             [20, 36, 0, 15, 7, 4, 9, 17, 19, 26])