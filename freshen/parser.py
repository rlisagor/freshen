#-*- coding: utf8 -*-

# This line ensures that frames from this file will not be shown in tracebacks
__unittest = 1

from pyparsing import *
import copy
import logging
import os
import re
import textwrap

try:
    from os.path import relpath
except Exception, e:
    from freshen.compat import relpath

log = logging.getLogger('freshen')

class Feature(object):
    
    def __init__(self, tags, name, description, scenarios):
        self.tags = tags
        self.name = name
        self.description = description
        self.scenarios = scenarios
        
        for sc in scenarios:
            sc.feature = self
        
    def __repr__(self):
        return '<Feature "%s": %d scenario(s)>' % (self.name, len(self.scenarios))

    def iter_scenarios(self):
        for sco in self.scenarios:
            for sc in sco.iterate():
                yield sc


class Scenario(object):
    
    def __init__(self, tags, name, steps):
        self.tags = tags
        self.name = name
        self.steps = steps
    
    def __repr__(self):
        return '<Scenario "%s">' % self.name

    def get_tags(self):
        return self.tags + self.feature.tags

    def iterate(self):
        yield self


class ScenarioOutline(Scenario):
    
    def __init__(self, tags, name, steps, examples):
        self.examples = examples
        super(ScenarioOutline, self).__init__(tags, name, steps)
    
    def __repr__(self):
        return '<ScenarioOutline "%s">' % self.name
    
    def iterate(self):
        for ex in self.examples:
            for values in ex.table.iterrows():
                new_steps = []
                for step in self.steps:
                    new_steps.append(step.set_values(values))
                sc = Scenario(self.tags, self.name, new_steps)
                sc.feature = self.feature
                yield sc


class Step(object):
    
    def __init__(self, step_type, match, arg=None):
        self.step_type = step_type
        self.match = match
        self.arg = arg
    
    def __repr__(self):
        return '<%s "%s">' % (self.step_type, self.match)
    
    def source_location(self, absolute=True):
        p = relpath(self.src_file, os.getcwd()) if absolute else self.src_file
        return '%s:%d' % (p, self.src_line)
    
    def set_values(self, value_dict):
        result = copy.deepcopy(self)
        for name, value in value_dict.iteritems():
            result.match = result.match.replace("<%s>" % name, value)
        return result


class Examples(object):

    def __init__(self, name, table):
        self.name = name
        self.table = table


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


def grammar(fname, l, convert=True, base_line=0):
    # l = language
    
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
        
    def process_string(s):
        return s[0].strip()
    
    def process_m_string(s):
        return textwrap.dedent(s[0])
    
    def process_tag(s):
        return s[0].strip("@")
    
    empty_not_n    = empty.copy().setWhitespaceChars(" \t")
    tags           = OneOrMore(Word("@", alphanums + "_").setParseAction(process_tag))
    
    following_text = empty_not_n + restOfLine + Suppress(lineEnd)
    section_header = lambda name: Suppress(name + ":") + following_text
    
    section_name   = Literal(l.word("scenario")) | Literal(l.word("scenario_outline"))
    descr_block    = Group(SkipTo(section_name | tags).setParseAction(process_descr))
    
    table_row      = Group(Suppress("|") +
                           delimitedList(Suppress(empty_not_n) +
                                         CharsNotIn("|\n").setParseAction(process_string) +
                                         Suppress(empty_not_n), delim="|") +
                           Suppress("|"))
    table          = table_row + Group(OneOrMore(table_row))
    
    m_string       = (Suppress(Literal('"""') + lineEnd).setWhitespaceChars(" \t") +
                      SkipTo((lineEnd +
                              Literal('"""')).setWhitespaceChars(" \t")).setWhitespaceChars("") +
                      Suppress('"""'))
    m_string.setParseAction(process_m_string)
    
    step_name      = Keyword(l.word('given')) | Keyword(l.word('when')) | Keyword(l.word('then')) | Keyword(l.word('and'))
    step           = step_name + following_text + Optional(table | m_string)
    steps          = Group(ZeroOrMore(step))

    example        = section_header(l.word('examples')) + table
    
    scenario       = Group(Optional(tags)) + section_header(l.word('scenario')) + steps
    scenario_outline = Group(Optional(tags)) + section_header(l.word('scenario_outline')) + steps + Group(OneOrMore(example))
    
    feature        = (Group(Optional(tags)) +
                      section_header(l.word('feature')) +
                      descr_block +
                      Group(OneOrMore(scenario | scenario_outline)))
    
    # Ignore tags for now as they are not supported
    feature.ignore(pythonStyleComment)
    steps.ignore(pythonStyleComment)
    
    if convert:
        table.setParseAction(create_object(Table))
        step.setParseAction(create_object(Step))
        scenario.setParseAction(create_object(Scenario))
        scenario_outline.setParseAction(create_object(ScenarioOutline))
        example.setParseAction(create_object(Examples))
        feature.setParseAction(create_object(Feature))
    
    return feature, steps

def parse_file(fname, language, convert=True):
    feature, _ = grammar(fname, language, convert)
    if convert:
        return feature.parseFile(fname)[0]
    else:
        return feature.parseFile(fname)

def parse_steps(spec, fname, base_line, language, convert=True):
    _, steps = grammar(fname, language, convert, base_line)
    if convert:
        return steps.parseString(spec)[0]
    else:
        return steps.parseString(spec)

