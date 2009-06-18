from pyparsing import *
import re
import copy

import logging
log = logging.getLogger('nose.plugins')

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

    def iter_scenarios(self):
        for sco in self.scenarios:
            for sc in sco.iterate():
                yield sc


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
    
    def __init__(self, step_type, match, arg=None):
        self.step_type = step_type
        self.match = match
        self.arg = arg
    
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


def grammar(fname, convert=True, base_line=0):
    
    def create_object(klass):
        def untokenize(s, loc, toks):
            result = []
            for t in toks:
                if isinstance(t, ParseResults):
                    t = t.asList()
                result.append(t)
            obj = klass(*result)
            obj.src_file = fname
            obj.src_line = base_line + lineno(loc, s)
            return obj
        return untokenize

    def process_descr(s):
        return [p.strip() for p in s[0].strip().split("\n")]
        
    def process_m_string(s):
        return s[0].strip()
    
    following_text = empty + restOfLine
    section_header = lambda name: Suppress(name + ":") + following_text
    
    section_name   = Literal("Scenario") | Literal("Scenario Outline")
    descr_block    = Group(SkipTo(section_name).setParseAction(process_descr))
    
    empty_not_n    = empty.copy().setWhitespaceChars(" \t")
    table_row      = Group(Suppress("|") +
                           delimitedList(Suppress(empty_not_n) +
                                         CharsNotIn("| \t\n") +
                                         Suppress(empty_not_n), delim="|") +
                           Suppress("|"))
    table          = table_row + Group(OneOrMore(table_row))
    
    m_string       = QuotedString('"""', multiline=True, unquoteResults=True).setParseAction(process_m_string)
    
    step_name      = Keyword("Given") | Keyword("When") | Keyword("Then") | Keyword("And")
    step           = step_name + following_text + Optional(table | m_string)
    steps          = Group(OneOrMore(step))

    examples       = Suppress("Examples:") + table
    
    scenario       = section_header("Scenario") + steps
    scenario_outline = section_header("Scenario Outline") + steps + examples
    
    feature        = section_header("Feature") + descr_block + Group(OneOrMore(scenario | scenario_outline))
    
    # Ignore tags for now as they are not supported
    tags           = OneOrMore("@" + Word(alphanums + "_"))
    feature.ignore(tags).ignore(pythonStyleComment)
    steps.ignore(tags).ignore(pythonStyleComment)
    
    if convert:
        table.setParseAction(create_object(Table))
        step.setParseAction(create_object(Step))
        scenario.setParseAction(create_object(Scenario))
        scenario_outline.setParseAction(create_object(ScenarioOutline))
        feature.setParseAction(create_object(Feature))
    
    return feature, steps

def parse_file(fname, convert=True):
    feature, _ = grammar(fname, convert)
    if convert:
        return feature.parseFile(fname)[0]
    else:
        return feature.parseFile(fname)

def parse_steps(spec, fname, base_line, convert=True):
    _, steps = grammar(fname, convert, base_line)
    if convert:
        return steps.parseString(spec)[0]
    else:
        return steps.parseString(spec)

