#-*- coding: utf8 -*-
from freshen import *
from freshen.checks import *

import calculator

@Before
def before(sc):
    scc.calc = calculator.Calculator()
    scc.result = None

@Given("le nombre (\d+) entré dans la calculatrice")
def enter(num):
    scc.calc.push(int(num))

@When("j'appuie sur (\w+)")
def press(button):
    op = getattr(scc.calc, button)
    scc.result = op()

@Then("le résultat doit être (.*) à l'écran")
def check_result(value):
    assert_equal(str(scc.result), value)

