#!/usr/bin/python

import parser
import pprint

print parser.parse_file("test/features/addition.feature")
print parser.parse_file("test/features/division.feature")

