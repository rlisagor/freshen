from nose.tools import *
from freshen import *

import calculator

@Before
def before(sc):
    global calc
    global result
    calc = calculator.Calculator()
    result = None

@Given("I have entered (\d+) into the calculator")
def enter(num):
    calc.push(int(num))

@When("I press (\w+)")
def press(button):
    global result
    op = getattr(calc, button)
    result = op()

@Then("the result should be (.*) on the screen")
def check_result(value):
    assert_equal(str(result), value)

