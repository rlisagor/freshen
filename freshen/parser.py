from pyparsing import *
import re
import copy


class Feature(object):
    
    def __init__(self, name, description, scenarios):
        self.name = name
        self.description = description
        self.scenarios = scenarios
        
    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % (self.name, len(self.scenarios))

    def dump(self, expand=False):
        print "Feature: %s" % self.name
        for line in self.description:
            print "   ", line
        print
        for sco in self.scenarios:
            if expand:
                for sc in sco.iterate():
                    sc.dump()
            else:
                sco.dump()

class Scenario(object):
    
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps
    
    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def iterate(self):
        yield self

    def dump(self):
        print "    Scenario:", self.name
        for s in self.steps:
            s.dump()
        print

class ScenarioOutline(object):
    
    def __init__(self, name, steps, examples):
        self.name = name
        self.steps = steps
        self.examples = examples

    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name
    
    def iterate(self):
        for values in self.examples.iterrows():
            new_steps = []
            for step in self.steps:
                new_steps.append(step.set_values(values))
            yield Scenario(self.name, new_steps)

    def dump(self):
        print "    Scenario Outline:", self.name
        for s in self.steps:
            s.dump()
        print
        self.examples.dump()

class Step(object):
    
    def __init__(self, step_type, match):
        self.step_type = step_type
        self.match = match
    
    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.match)

    def set_values(self, value_dict):
        result = copy.deepcopy(self)
        for name, value in value_dict.iteritems():
            result.match = result.match.replace("<%s>" % name, value)
        return result

    def dump(self):
        print "       ", self.step_type, self.match


class Table(object):
    
    def __init__(self, headings, rows):
        assert [len(r) == len(headings) for r in rows], "Malformed table"
        
        self.headings = headings
        self.rows = rows

    def __repr__(self):
        return "<Table: %dx%d>" % (len(self.headings), len(self.rows))

    def iterrows(self):
        for row in self.rows:
            yield dict(zip(self.headings, row))

    def dump(self):
        print "    Examples:"
        all_rows = [self.headings] + self.rows
        for r in all_rows:
            print "        | " + " | ".join(r) + " |"
        print

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

def parse_file(fname):
    fp = open(fname)
    r = parse(fp.read())
    fp.close()
    return r

