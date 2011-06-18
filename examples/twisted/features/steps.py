from freshen import When, Then, scc
from twisted.internet import reactor
from twisted.internet.defer import Deferred

@When("^I implement a step that returns a twisted Deferred object$")
def async_step():
    scc.state = 'executing'
    def return_async_result(result):
        scc.state = result
    deferred = Deferred()
    reactor.callLater(1, deferred.callback, 'done')
    deferred.addCallback(return_async_result)
    return deferred

@Then("^freshen will wait for the result before executing the next step$")
def check_async_execution():
    assert scc.state == 'done', \
           'Freshen did not wait for async ' \
           'test to be finished before executing ' \
           'the next step.'

