import unittest

import sys

from freshen.noseplugin import FreshenNosePlugin
from optparse import OptionParser

class TestFreshenTestCaseName(unittest.TestCase):

    def test_should_subclass_FreshenTestCase_with_feature_name(self):
        plugin = FreshenNosePlugin()
        parser = OptionParser()

        plugin.options(parser, {})

        sys.argv = ['nosetests', '--with-freshen']
        (options, args) = parser.parse_args()

        plugin.configure(options, None)

        test_generator = plugin.loadTestsFromFile('resources/valid_no_tags_no_use_only.feature')
        test_instance = test_generator.next()

        self.assertEquals(test_instance.__class__.__name__, 'Independence of the counter.')
