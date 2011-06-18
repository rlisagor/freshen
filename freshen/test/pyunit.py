#-*- coding: utf8 -*-

from freshen.test.base import FreshenTestCase

from unittest import TestCase


class PyunitTestCase(FreshenTestCase, TestCase):
    """Support PyUnit tests."""

    def __init__(self, step_runner, step_registry, feature, scenario, feature_suite):
        FreshenTestCase.__init__(self, step_runner, step_registry,
                                 feature, scenario, feature_suite)
        TestCase.__init__(self)

    def runTest(self):
        for step in self.scenario.iter_steps():
            self.runStep(step, 3)
        self.last_step = None
