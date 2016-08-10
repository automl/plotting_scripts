import itertools
import unittest

from plottingscripts.utils import plot_util


class plotUtilTest(unittest.TestCase):

    def test_get_empty_iterator(self):
        iter_ = plot_util.get_empty_iterator()
        self.assertEqual(iter_.next(), None)
        self.assertIsInstance(iter_, itertools.cycle)

    def test_get_plot_markers(self):
        iter_ = plot_util.get_plot_markers()
        self.assertIsInstance(iter_, itertools.cycle)

    def test_get_plot_linestyles(self):
        iter_ = plot_util.get_plot_linestyles()
        self.assertIsInstance(iter_, itertools.cycle)

    def test_get_single_linestyle(self):
        iter_ = plot_util.get_single_linestyle()
        self.assertIsInstance(iter_, itertools.cycle)

    def test_get_plot_colors(self):
        iter_ = plot_util.get_plot_colors()
        self.assertIsInstance(iter_, itertools.cycle)

    def test_get_defaults(self):
        defaults = plot_util.get_defaults()
        self.assertEqual(len(defaults), 11)
        for key in ("linestyles", "colors", "markers", "markersize",
                  "labelfontsize", "linewidth", "titlefontsize",
                  "gridcolor", "gridalpha", "dpi", "legendsize"):
            self.assertTrue(key in defaults)

    def test_fill_with_defaults(self):
        filled = plot_util.fill_with_defaults({})
        for key in ("linestyles", "colors", "markers", "markersize",
                    "labelfontsize", "linewidth", "titlefontsize",
                    "gridcolor", "gridalpha", "dpi", "legendsize"):
            self.assertTrue(key in filled)

        filled = plot_util.fill_with_defaults({'dpi': 50})
        self.assertEqual(filled['dpi'], 50)

        filled = plot_util.fill_with_defaults({'thiskeydoesnotexist': 23})
        self.assertEqual(filled['thiskeydoesnotexist'], 23)

    @unittest.skip("'test_save_plot' not yet implemented")
    def test_save_plot(fig, save, dpi):
        pass