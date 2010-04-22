#-*- coding: utf8 -*-

from freshen.cuke import FreshenHandler
import sys
import traceback

COLORS = {
    'bold': '1',
    'grey': '2',
    'underline': '4',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'white': '37'
}

UNDEFINED = 'yellow'
AMBIGUOUS = 'cyan'
FAILED = 'red'
ERROR = 'red,bold'
PASSED = 'green'
TAG = 'cyan'
COMMENT = 'grey'

def colored(text, colorspec):
    colors = [c.strip() for c in colorspec.split(',')]
    result = ""
    for c in colors:
        result += "\033[%sm" % COLORS[c]
    result += text + "\033[0m"
    return result

class ConsoleHandler(FreshenHandler):
    
    def before_feature(self, feature):
        if feature.tags:
            print colored(" ".join(('@' + t) for t in feature.tags), TAG)
        print 'Feature:', feature.name
        if feature.description != ['']:
            print "\n".join(('    ' + l) for l in feature.description)
            print
    
    def before_scenario(self, scenario):
        if scenario.tags:
            print '    ' + colored(" ".join(('@' + t) for t in scenario.tags), TAG)
        print "    Scenario:", scenario.name
    
    def after_scenario(self, scenario):
        print
    
    def _step(self, step, color):
        print "        " + colored('%-40s' % (step.step_type + " " + step.match), color) + \
                           colored(" # " + step.source_location(), COMMENT)
    
    def step_failed(self, step, e):
        self._step(step, FAILED)
    
    def step_ambiguous(self, step, e):
        self._step(step, AMBIGUOUS)
        
    def step_undefined(self, step, e):
        self._step(step, UNDEFINED)
    
    def step_exception(self, step, e):
        self._step(step, ERROR)
    
    def after_step(self, step):
        self._step(step, PASSED)


