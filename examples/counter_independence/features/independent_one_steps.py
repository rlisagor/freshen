"""
Independant steps for one.
"""

from freshen import *
from freshen.checks import *

from examples.counter_independence import counter

@Before
def before(sc):
    counter.increment_counter()

@After
def after(sc):
    counter.reset_counter()

@Then("the counter prints (\d+).")
def check_counter(number):
    assert_equal(counter.get_counter(), int(number))
