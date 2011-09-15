import unittest

import sys

from freshen.noseplugin import FreshenNosePlugin
from optparse import OptionParser

class TestFreshenTestCaseName(unittest.TestCase):

    def _make_plugin(self):
        plugin = FreshenNosePlugin()
        parser = OptionParser()

        plugin.options(parser, {})

        sys.argv = ['nosetests', '--with-freshen']
        (options, args) = parser.parse_args()

        plugin.configure(options, None)
        return plugin

    def test_should_use_feature_name_as_class_name_when_subclassing_FreshenTestCase(self):
        plugin = self._make_plugin()
        test_generator = plugin.loadTestsFromFile('./resources/valid_no_tags_no_use_only.feature')
        test_instance = test_generator.next()

        self.assertEquals(test_instance.__class__.__name__, 'Independence of the counter.')

    def test_should_use_scenario_name_as_method_name_when_subclassing_FreshenTestCase(self):
        plugin = self._make_plugin()
        test_generator = plugin.loadTestsFromFile('./resources/valid_no_tags_no_use_only.feature')
        test_instance = test_generator.next()

        self.assertNotEqual(getattr(test_instance, 'Print counter', None), None)
