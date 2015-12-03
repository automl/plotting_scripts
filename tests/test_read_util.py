from mock import mock_open
import unittest

from plottingscripts.utils import read_util


class plotUtilTest(unittest.TestCase):

    def test_get_empty_iterator(self):
        with patch('__main__.open', mock_open(read_data='bibble'), create=True) as m:

