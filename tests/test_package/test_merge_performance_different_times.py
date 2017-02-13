import os
import sys
import unittest

sys.path.append(os.path.join(__file__, "../plottingscripts"))
import plottingscripts.utils.merge_test_performance_different_times as mdt

class plotUtilTest(unittest.TestCase):

    def test_fill_array_regular(self):
        time_a = [0.5, 1, 2, 3, 4]
        value_a = [10, 9, 8, 7, 6]
        time_b = [0.5, 2.5, 3]
        value_b = [5, 4, 2]
        v, t = mdt.fill_trajectory(performance_list=(value_a, value_b),
                                   time_list=(time_a, time_b))
        ti_should = [ 0.5, 1.0, 2.0, 2.5, 3.0, 4.0]
        va_should = [10.0, 9.0, 8.0, 8.0, 7.0, 6.0]
        vb_should = [ 5.0, 5.0, 5.0, 4.0, 2.0, 2.0]

        self.assertListEqual(ti_should, list(t))
        self.assertListEqual(va_should, list(v[:, 0]))
        self.assertListEqual(vb_should, list(v[:, 1]))

    def test_fill_array_one_empty(self):
        time_a = []
        value_a = []
        time_b = [0.5, 2.5, 3]
        value_b = [5, 4, 2]
        self.assertRaises(ValueError, mdt.fill_trajectory,
                          performance_list=(value_a, value_b),
                          time_list=(time_a, time_b))

    def test_fill_array_non_overlapping(self):
        time_a = [0.5, 1, 2, 3, 4]
        value_a = [10, 9, 8, 7, 6]
        time_b = [100, 110, 111]
        value_b = [5, 4, 2]
        self.assertRaises(ValueError, mdt.fill_trajectory,
                          performance_list=(value_a, value_b),
                          time_list=(time_a, time_b))
        v, t = mdt.fill_trajectory(performance_list=(value_a, value_b),
                                   time_list=(time_a, time_b),
                                   replace_nan=1)
        ti_should = [ 0.5, 1.0, 2.0, 3.0, 4.0, 100.0, 110.0, 111.0]
        va_should = [10.0, 9.0, 8.0, 7.0, 6.0,   6.0,   6.0,   6.0]
        vb_should = [ 1.0, 1.0, 1.0, 1.0, 1.0,   5.0,   4.0,   2.0]

        self.assertListEqual(ti_should, list(t))
        self.assertListEqual(va_should, list(v[:, 0]))
        self.assertListEqual(vb_should, list(v[:, 1]))

    def test_fill_array_1d_list(self):
        time_a = [0.5,]
        value_a = [10,]
        time_b = [100,]
        value_b = [5,]
        self.assertRaises(ValueError, mdt.fill_trajectory,
                          performance_list=(value_a, value_b),
                          time_list=(time_a, time_b))
        v, t = mdt.fill_trajectory(performance_list=(value_a, value_b),
                                   time_list=(time_a, time_b),
                                   replace_nan=1)
        ti_should = [ 0.5, 100.0]
        va_should = [10.0,  10.0]
        vb_should = [ 1.0,   5.0]

        self.assertListEqual(ti_should, list(t))
        self.assertListEqual(va_should, list(v[:, 0]))
        self.assertListEqual(vb_should, list(v[:, 1]))

    def test_fill_array_array_mismatch(self):
        time_a = [0.5, 2]
        value_a = [10,]
        time_b = [100,]
        value_b = [5,]
        self.assertRaisesRegexp(ValueError, "Array length mismatch",
                                mdt.fill_trajectory,
                                performance_list=(value_a, value_b),
                                time_list=(time_a, time_b))