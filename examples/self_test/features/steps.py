from freshen import *
from nose.tools import *

def flunker(runner):
    raise Exception("FAIL")


@Given("^passing$")
def passing(runner, table):
    pass

@Given("^failing$")
def failing(runner, string):
    flunker(runner)

@Given("^passing without a table$")
def pass_without_table(runner):
    pass

@Given("^failing without a table$")
def fail_without_table(runner):
    flunker(runner)

@Given("^a step definition that calls an undefined step$")
def call_undef(runner):
    run_steps("Given this does not exist")

@Given("^call step \"(.*)\"$")
def call_step(runner, step):
    run_steps("Given step")

@Given("^'(.+)' cukes$")
def do_cukes(runner, c):
    if glc.cukes:
        raise Exception("We already have %s cukes!" % glc.cukes)
    glc.cukes = c

@Then("^I should have '(.+)' cukes$")
def should_have_cukes(runner, c):
    assert_equals(c, glc.cukes)

@Given("^'(.+)' global cukes$")
def global_cukes(runner, c):
    if scc.scenario_runs >= 1:
        flunker(runner)
    
    glc.cukes = c
    scc.scenario_runs += 1

@Then("^I should have '(.+)' global cukes$")
def check_global_cukes(runner, c):
    assert_equals(c, glc.cukes)

@Given("^table$")
def with_table(runner, table):
    scc.t = table

@Given("^multiline string$")
def with_m_string(runner, string):
    scc.multiline = string

@Then("^the table should be$")
def check_table(runner, table):
    assert_equals(scc.t, table)

@Then("^the multiline string should be$")
def check_m_string(runner, string):
    assert_equals(scc.multiline)

@Given("^failing expectation$")
def failing_expectations(runner):
    assert_equals('this', 'that')

@Given("^unused$")
def unused(runner):
    pass

@Given("^another unused$")
def another_unused(runner):
    pass

