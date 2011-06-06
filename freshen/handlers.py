#-*- coding: utf8 -*-

from freshen.cuke import FreshenHandler
from freshen.prettyprint import FreshenPrettyPrint

class ConsoleHandler(FreshenHandler):
    
    def before_feature(self, feature):
        print FreshenPrettyPrint.feature(feature)
        print
    
    def before_scenario(self, scenario):
        print FreshenPrettyPrint.scenario(scenario)
    
    def after_scenario(self, scenario):
        print
    
    def step_failed(self, step, e):
        print FreshenPrettyPrint.step_failed(step)
    
    def step_ambiguous(self, step, e):
        print FreshenPrettyPrint.step_ambiguous(step)
        
    def step_undefined(self, step, e):
        print FreshenPrettyPrint.step_undefined(step)
    
    def step_exception(self, step, e):
        print FreshenPrettyPrint.step_exception(step)
    
    def after_step(self, step):
        print FreshenPrettyPrint.step_passed(step)


