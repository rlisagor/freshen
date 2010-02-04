from freshen import *
from freshen.checks import *

import calculator

@Before
def before(runner, sc):
    scc.calc = calculator.Calculator()
    scc.result = None

@Given("I have entered (\d+) into the calculator")
def enter(runner, num):
    scc.calc.push(int(num))

@When("I press (\w+)")
def press(runner, button):
    op = getattr(scc.calc, button)
    scc.result = op()

@Then("the result should be (.*) on the screen")
def check_result(runner, value):
    assert_equal(str(scc.result), value)

