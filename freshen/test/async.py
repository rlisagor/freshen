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

    def setUp(self):
        """Initialize the test."""
        super(TwistedTestCase, self).setUp()
        hooks = []
        for hook_impl in \
        self.step_registry.get_hooks('before', self.scenario.get_tags()):
            hooks.append(lambda hook=hook_impl: hook.run(self.scenario))
        return self._run_deferred(hooks)

    @inlineCallbacks
    def runTest(self):
        """Run the test."""
        steps = []
        for step in self.scenario.iter_steps():
            steps.append(lambda s=step: self.runStep(s, 3))
        yield self._run_deferred(steps)
        self.last_step = None

    def tearDown(self):
        """Clean up after the test."""
        hooks = []
        for hook_impl in reversed(\
        self.step_registry.get_hooks('after', self.scenario.get_tags())):
            hooks.append(lambda hook=hook_impl: hook_impl.run(self.scenario))
        return self._run_deferred(hooks)

    @inlineCallbacks
    def _run_deferred(self, callbacks):
        """Create a chain of deferred function calls
        and events.
        
        Returns: Deferred"""
        start_chain = Deferred()
        deferreds = [start_chain]

        for callback in callbacks:
            result = callback()
            if isinstance(result, Deferred):
                # Collect deferred events
                deferreds.append(result)
            elif callable(result):
                # Collect deferred function calls
                deferreds[-1].addCallback(result)

        # Trigger the deferred execution chain.
        start_chain.callback(None)

        # Wait for async events.
        for deferred in deferreds:
            yield deferred

