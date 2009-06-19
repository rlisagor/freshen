from freshen import *
from nose.tools import *

import os
import commands

status = None
output = None

def before():
    os.chdir("examples/self_test")
    
@When("^I run nose (.+)$")
def run_nose(args):
    global status, output
    status, output = commands.getstatusoutput("nosetests --with-freshen " + args)

@Then("^it should (pass|fail)$")
def check_outcome(exp_status):
    if exp_status == "fail":
        assert status != 0
    elif status != 0:
        raise Exception("Failed with exit status %d\nOUTPUT:\n%s" % (result, output))

@Then("^it should (pass|fail) with$")
def check_outcome(exp_output, exp_status):
    run_steps("Then it should %s" % exp_status)
    assert_equals(exp_output, output)
    
