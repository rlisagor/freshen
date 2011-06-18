#-*- coding: utf8 -*-

from freshen.test.base import FreshenTestCase

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, Deferred

class TwistedTestCase(FreshenTestCase, TestCase):
    """Support asynchronous feature tests."""

    # pylint: disable=R0913
    def __init__(self, step_runner, step_registry,
                 feature, scenario, feature_suite):
        FreshenTestCase.__init__(self, step_runner, step_registry,
                                 feature, scenario, feature_suite)
        TestCase.__init__(self)

    @inlineCallbacks
    def runTest(self):
        for step in self.scenario.iter_steps():
            result = self.runStep(step)
            if isinstance(result, Deferred):
                yield result
        self.last_step = None
