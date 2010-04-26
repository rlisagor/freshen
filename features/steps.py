from freshen import *
from freshen.checks import *

import os
import shlex
import subprocess
import re

@Before
def before(scenario):
    scc.cwd = os.getcwd()
    scc.is_traceback = False
    
@Before('traceback_not_important')
def set_eliminate_traceback(scenario):
    scc.is_traceback = True

@When("^I run nose (.+)$")
def run_nose(args):
    args_list = shlex.split(args)
    command = ['nosetests', '--with-freshen'] + args_list 
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    scc.output, _ = process.communicate()
    scc.status = process.returncode
    scc.output = _normalize_newlines(scc.output) 
    scc.output = scc.output.rstrip()
    _extract_time_and_traceback()
    
_newlines_re = re.compile(r'(\r\n|\r|\r)')
def _normalize_newlines(string):
    return _newlines_re.sub('\n', string)

def _extract_time_and_traceback():
    scc.time = _get_time_in_output_result(scc.output)
    if scc.is_traceback:
        scc.traceback = _get_traceback_in_output_result(scc.output)

_time_re = re.compile(r'\d+\.\d+s')
def _get_time_in_output_result(string):
    times = re.findall(_time_re, string)
    return times[0]

_traceback_re = re.compile(r'Traceback(.+)' 
                           + r'\n' + ('-' * 70),
                           re.DOTALL)
def _get_traceback_in_output_result(string):
    tracebacks = re.findall(_traceback_re, string)
    return tracebacks[0]



@Then("^it should (pass|fail)$")
def check_outcome(exp_status):
    if exp_status == "fail":
        assert_not_equals(scc.status, 0)
    elif scc.status != 0:
        raise Exception("Failed with exit status %d\nOUTPUT:\n%s" % (scc.status, scc.output))

@Then("^it should (pass|fail) with$")
def check_outcome_with(exp_output, exp_status):
    run_steps("Then it should %s" % exp_status)
    
    exp_output = exp_output.replace("{cwd}", scc.cwd)
    exp_output = exp_output.replace("{time}", scc.time)
    exp_output = exp_output.replace("{sep}", os.sep)
    if scc.is_traceback:
        exp_output = exp_output.replace("{traceback_trace}", scc.traceback)
    assert_equals(exp_output, scc.output)

