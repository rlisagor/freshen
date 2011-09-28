#-*- coding: utf8 -*-

from freshen.test.base import FreshenTestCase

from unittest import TestCase

def make_pyunit_testcase_class(base_test_case_class):

    class _PyunitTestCase(FreshenTestCase, base_test_case_class):
        """Support PyUnit tests."""

        def __init__(self, step_runner, step_registry, feature, scenario, feature_suite):
            FreshenTestCase.__init__(self, step_runner, step_registry,
                                     feature, scenario, feature_suite)
            base_test_case_class.__init__(self, scenario.name)

        def setUp(self):
            super(_PyunitTestCase, self).setUp()
            for hook_impl in self.step_registry.get_hooks('before', self.scenario.get_tags()):
                hook_impl.run(self.scenario)

        def runScenario(self):
            for step in self.scenario.iter_steps():
                self.runStep(step, 3)
            self.last_step = None

        def tearDown(self):
            for hook_impl in reversed(self.step_registry.get_hooks('after', self.scenario.get_tags())):
                hook_impl.run(self.scenario)

    return _PyunitTestCase

PyunitTestCase = make_pyunit_testcase_class(TestCase)
