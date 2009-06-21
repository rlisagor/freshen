from freshen import *
from nose.tools import *

def flunker():
    raise Exception("FAIL")


@Given("^passing$")
def passing(table):
    pass

@Given("^failing$")
def failing(string):
    flunker()

@Given("^passing without a table$")
def pass_without_table():
    pass

@Given("^failing without a table$")
def fail_without_table():
    flunker()

@Given("^a step definition that calls an undefined step$")
def call_undef():
    run_steps("Given this does not exist")

@Given("^call step \"(.*)\"$")
def call_step(step):
    run_steps("Given step")

@Given("^'(.+)' cukes$")
def do_cukes(c):
    if glc.cukes:
        raise Exception("We already have %s cukes!" % glc.cukes)
    glc.cukes = c

@Then("^I should have '(.+)' cukes$")
def should_have_cukes(c):
    assert_equals(c, glc.cukes)

@Given("^'(.+)' global cukes$")
def global_cukes(c):
    if scc.scenario_runs >= 1:
        flunker()
    
    glc.cukes = c
    scc.scenario_runs += 1

@Then("^I should have '(.+)' global cukes$")
def check_global_cukes(c):
    assert_equals(c, glc.cukes)

@Given("^table$")
def with_table(table):
    scc.t = table

@Given("^multiline string$")
def with_m_string(string):
    scc.multiline = string

@Then("^the table should be$")
def check_table(table):
    assert_equals(scc.t, table)

@Then("^the multiline string should be$")
def check_m_string(string):
    assert_equals(scc.multiline)

@Given("^failing expectation$")
def failing_expectations():
    assert_equals('this', 'that')

@Given("^unused$")
def unused():
    pass

@Given("^another unused$")
def another_unused():
    pass

