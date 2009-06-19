from freshen import *
from freshen.checks import *

import os
import commands
import re

status = None
output = None
orig_dir = None
cwd = None

@Before
def before():
    global orig_dir, cwd
    orig_dir = os.getcwd()
    os.chdir("examples/self_test")
    cwd = os.getcwd()

@After
def after():
    global orig_dir, cwd
    os.chdir(orig_dir)
    cwd = os.getcwd()
    orig_dir = None

@When("^I run nose (.+)$")
def run_nose(args):
    global status, output
    status, output = commands.getstatusoutput("nosetests --with-freshen " + args)
    output = re.sub(r"(Ran \d+ tests? in )([\d.]+)s", r"\1{time}", output)

@Then("^it should (pass|fail)$")
def check_outcome(exp_status):
    if exp_status == "fail":
        assert_not_equals(status, 0)
    elif status != 0:
        raise Exception("Failed with exit status %d\nOUTPUT:\n%s" % (result, output))

@Then("^it should (pass|fail) with$")
def check_outcome(exp_output, exp_status):
    run_steps("Then it should %s" % exp_status)
    
    exp_output = exp_output.replace("{cwd}", cwd)
    assert_equals(exp_output, output)

