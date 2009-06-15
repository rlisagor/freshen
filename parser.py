from pyparsing import *


def parse_file(fname):
    fp = open(fname)
    r = parse(fp.read())
    fp.close()
    return r

def parse(text):
    following_text = empty + restOfLine + Suppress(lineEnd)
    section_header = lambda name: Suppress(name + ":") + following_text

    descr_line     = ~section_header("Scenario") + ~section_header("Scenario Outline") + following_text
    descr_block    = Group(OneOrMore(descr_line))

    table_row      = Group(Suppress("|") + delimitedList(Regex("[^\|\s]+"), delim="|") + Suppress("|"))
    table          = OneOrMore(table_row)

    step           = lambda t: Keyword(t) + following_text
    steps          = Group(
                         step("Given") + ZeroOrMore(step("And")) +
                         step("When") + ZeroOrMore(step("And")) +
                         step("Then") + ZeroOrMore(step("And")))
    examples       = Suppress("Examples:") + table

    scenario       = section_header("Scenario") + steps
    scenario_outline = section_header("Scenario Outline") + steps + examples

    feature        = section_header("Feature") + descr_block + OneOrMore(scenario | scenario_outline)
    
    return feature.parseString(text)

