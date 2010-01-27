from freshen import *
from freshen.checks import *

import os
import commands
import re

@Before
def before(runner, scenario):
    scc.orig_dir = os.getcwd()
    os.chdir("examples/self_test")
    scc.cwd = os.getcwd()

@After
def after(runner, scenario):
    os.chdir(scc.orig_dir)
    scc.cwd = os.getcwd()

@When("^I run nose (.+)$")
def run_nose(runner, args):
    scc.status, scc.output = commands.getstatusoutput("nosetests --with-freshen " + args)
    scc.output = re.sub(r"(Ran \d+ tests? in )([\d.]+)s", r"\1{time}", scc.output)

@Then("^it should (pass|fail)$")
def check_outcome(runner, exp_status):
    if exp_status == "fail":
        assert_not_equals(scc.status, 0)
    elif scc.status != 0:
        raise Exception("Failed with exit status %d\nOUTPUT:\n%s" % (scc.status, scc.output))

@Then("^it should (pass|fail) with$")
def check_outcome_and_status(runner, exp_output, exp_status):
    runner.run_steps_from_string("Then it should %s" % exp_status)
    
    exp_output = exp_output.replace("{cwd}", scc.cwd)
    assert_equals(exp_output, scc.output)

