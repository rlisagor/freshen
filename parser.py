from pyparsing import *


def parse_file(fname):
    fp = open(fname)
    r = parse(fp.read())
    fp.close()
    return r

class Feature(object):
    
    def __init__(self, name, description, scenarios):
        self.name = name
        self.description = description
        self.scenarios = scenarios
        
    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % (self.name, len(self.scenarios))

class Scenario(object):
    
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps
    
    def __repr__(self):
        return '<Scenario "%s">' % self.name

class ScenarioOutline(object):
    
    def __init__(self, name, steps, examples):
        self.name = name
        self.steps = steps
        self.examples = examples

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name

class Step(object):
    
    def __init__(self, step_type, match):
        self.step_type = step_type
        self.match = match
        
    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.match)

class Table(object):
    
    def __init__(self, headings, rows):
        self.headings = headings
        self.rows = rows


def create_object(klass):
    def untokenize(toks):
        result = []
        for t in toks:
            if isinstance(t, ParseResults):
                t = t.asList()
            result.append(t)
        return klass(*result)
    return untokenize

def parse(text):
    following_text = empty + restOfLine + Suppress(lineEnd)
    section_header = lambda name: Suppress(name + ":") + following_text

    descr_line     = ~section_header("Scenario") + ~section_header("Scenario Outline") + following_text
    descr_block    = Group(OneOrMore(descr_line))

    table_row      = Group(Suppress("|") + delimitedList(Regex("[^\|\s]+"), delim="|") + Suppress("|"))
    table          = (table_row + Group(OneOrMore(table_row))).setParseAction(create_object(Table))

    step           = lambda t: (Keyword(t) + following_text).setParseAction(create_object(Step))
    steps          = Group(
                         step("Given") + ZeroOrMore(step("And")) +
                         step("When") + ZeroOrMore(step("And")) +
                         step("Then") + ZeroOrMore(step("And")))
    
    examples       = Suppress("Examples:") + table

    scenario       = (section_header("Scenario") +
                      steps).setParseAction(create_object(Scenario))
    
    scenario_outline = (section_header("Scenario Outline") +
                        steps +
                        examples).setParseAction(create_object(ScenarioOutline))

    feature        = (section_header("Feature") +
                      descr_block +
                      Group(OneOrMore(scenario | scenario_outline))).setParseAction(create_object(Feature))
    
    return feature.parseString(text)[0]

