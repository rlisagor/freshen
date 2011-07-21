"""
Steps to simulate asynchronous events and function calls.
"""

from freshen import When, Then, scc
from twisted.internet import reactor
from twisted.internet.defer import Deferred

@When("^I implement a step that returns a twisted Deferred object$")
def simulate_async_event():
    """Simulate an asynchronous event."""
    scc.state = 'executing'
    def async_event(result):
        """All other asynchronous events or function calls
        returned from later steps will wait until this
        callback fires."""
        scc.state = result
        return 'some event result'
    deferred = Deferred()
    reactor.callLater(1, deferred.callback, 'done') # pylint: disable=E1101
    deferred.addCallback(async_event)
    return deferred

@Then("^freshen will wait for the result before executing the next step$")
def check_async_execution():
    """Simulate an asynchronous function call."""
    def async_function(result_from_prior_event):
        """This function will only be called after
        all events returned from previous steps have
        been executed."""
        assert scc.state == 'done', \
               'Freshen did not wait for async ' \
               'test to be finished before executing ' \
               'the next step.'
        assert result_from_prior_event == 'some event result', \
               'The result from a prior event was not correctly' \
               'passed into the asynchronous function call.'
    return async_function

