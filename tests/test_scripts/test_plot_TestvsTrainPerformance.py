import os
import unittest
import unittest.mock

import numpy as np

import scripts.plot_TestvsTrainPerformance


class Test_TestvsTrainPerformance(unittest.TestCase):

    def test_get_performance_data(self):
        # This is only a smoke test!
        this_dir = os.path.abspath(os.path.dirname(__file__))
        file_list = [['test_data/strategy-1_seed-1.csv',
                      'test_data/strategy-1_seed-2.csv'],
                     ['test_data/strategy-2_seed-1.csv',
                      'test_data/strategy-2_seed-2.csv']]
        file_list = [[os.path.join(this_dir, f) for f in f1] for f1 in file_list]

        name_list = ['strategy-1', 'strategy-2']
        maxvalue = 0.8

        name_list_test_train, new_time_list, performance = \
            scripts.plot_TestvsTrainPerformance.get_performance_data(
            file_list, name_list, maxvalue)

        self.assertEqual(['strategy-1_train', 'strategy-1_test',
                          'strategy-2_train', 'strategy-2_test'],
                         name_list_test_train)
        new_time_list_fixture = \
            [[0., 79.22711854, 79.2339509, 139.66280422, 160.31798997, 184.22010806],
             [0., 79.22711854, 79.2339509, 139.66280422, 160.31798997, 184.22010806],
             [0., 84.08260822, 85.16516638, 140.9176791, 163.20254068, 187.84066503],
             [0., 84.08260822, 85.16516638, 140.9176791, 163.20254068, 187.84066503]]
        np.testing.assert_allclose(new_time_list_fixture, new_time_list)
        performance_fixture = \
            [[[0.8, 0.49378051, 0.49378051, 0.4199422, 0.40854252, 0.1539956],
              [0.8, 0.8, 0.41945371, 0.41945371, 0.41945371, 0.41945371]],
             [[0.8, 0.45547531, 0.45547531, 0.32589195, 0.30603017, 0.13270133],
              [0.8, 0.8, 0.44087794, 0.44087794, 0.44087794, 0.44087794]],
             [[0.8, 0.49378051, 0.49378051, 0.4199422, 0.40854252, 0.1539956],
              [0.8, 0.8, 0.41945371, 0.41945371, 0.41945371, 0.41945371]],
             [[0.8, 0.45547531, 0.45547531, 0.32589195, 0.30603017, 0.13270133],
              [0.8, 0.8, 0.44087794, 0.44087794, 0.44087794, 0.44087794]]]
        np.testing.assert_allclose(performance_fixture, performance)
