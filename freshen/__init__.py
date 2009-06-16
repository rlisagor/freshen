#!/usr/bin/python

import parser
import pprint

add = parser.parse_file("test/features/addition.feature")
div = parser.parse_file("test/features/division.feature")

add.dump()


