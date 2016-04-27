#!/usr/bin/env python

#
# This file is part of MAD.
#
# MAD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MAD.  If not, see <http://www.gnu.org/licenses/>.
#


from unittest import TestCase
from tests.fakes import InMemoryFileSystem

from mad.ast.commons import *
from mad.ast.settings import *
from mad.ast.definitions import *
from mad.ast.actions import *

from mad.parsing import Parser, MADSyntaxError


class ParserTests(TestCase):

    MAD_FILE = "test.mad"

    def setUp(self):
        self.file_system = InMemoryFileSystem()

    def _do_parse(self, rule):
        parser = Parser(self.file_system, self.MAD_FILE)
        return parser.parse(entry_rule=rule, logger=None)


class CorrectExpressionTests(ParserTests):

    MAD_FILE = "test.mad"

    def setUp(self):
        self.file_system = InMemoryFileSystem()

    def test_parsing_all_expressions(self):
        for (text, expected_result, rule) in self._all_expressions():
            self.file_system.define(self.MAD_FILE, text)
            actual_result = self._do_parse(rule)
            self.assertEqual(expected_result, actual_result, "Fail to parse '%s'" % text)

    def _all_expressions(self):
        return [
            ("query DB/Select", Query("DB", "Select"), "query"),
            ("query DB/Select {timeout: 50}", Query("DB", "Select", timeout=50), "query"),
            ("query DB/Select {priority: 12}", Query("DB", "Select", priority=12), "query"),
            ("query DB/Select {priority: 12, timeout: 50}", Query("DB", "Select", priority=12, timeout=50), "query"),

            ("invoke DB/Select", Trigger("DB", "Select"), "invoke"),
            ("invoke DB/Select {priority: 12}", Trigger("DB", "Select", 12), "invoke"),

            ("think 5", Think(5), "think"),

            ("fail", Fail(), "fail"),
            ("fail 0.5", Fail(probability=0.5), "fail"),

            ("think 5 "
             "invoke DB/Select "
             "query DB/Insert "
             "ignore {"
             "  fail "
             "}",
             Sequence(
                Think(5),
                Trigger("DB", "Select"),
                Query("DB", "Insert"),
                IgnoreError(Fail())),
             "action_list"),

            ("retry { think 5 }",
             Retry(Think(5)),
             "retry"),

            ("retry (limit: 5) { think 5 }",
             Retry(Think(5), limit=5),
             "retry"),

            ("retry (delay: constant(10)) { think 5 }",
             Retry(Think(5), delay=Delay(10, "constant")),
             "retry"),

            ("retry (limit: 23, delay: exponential(135)) { think 5 }",
             Retry(Think(5), limit=23, delay=Delay(135, "exponential")),
             "retry"),

            ("ignore { think 5 }",
             IgnoreError(Think(5)),
             "ignore"
             ),

            ("operation Select { think 5 }",
             DefineOperation("Select", Think(5)),
             "define_operation"),

            ("service DB { operation Select { think 4 } }",
             DefineService("DB", DefineOperation("Select", Think(4))),
             "define_service"),

            ("client Browser { every 5 { query DB/Select } }",
             DefineClientStub("Browser", 5, Query("DB", "Select")),
             "define_client"),

            ("service DB { "
             "  operation Select { "
             "      think 4 "
             "  }"
             "}"
             "client Browser { "
             "  every 5 { "
             "      query DB/Select"
             "  }"
             "}",
             Sequence(DefineService("DB", DefineOperation("Select", Think(4))),
                      DefineClientStub("Browser", 5, Query("DB", "Select"))),
             "unit"),

            ("settings { queue: LIFO }", Settings(queue=LIFO()), "settings"),

            ("autoscaling {"
             "  period: 134"
             "  limits: [27, 52]"
             "}",
             {"autoscaling": Autoscaling(period=134, limits=(27, 52))},
             "autoscaling"),

            ("throttling: none",
             {"throttling": NoThrottlingSettings()},
             "throttling"),

            ("throttling: tail-drop(50)",
             {"throttling": TailDropSettings(capacity=50)},
             "throttling"),

            ("settings {"
             "  queue: FIFO"
             "  autoscaling {"
             "      limits: [1, 5]"
             "  }"
             "  throttling: tail-drop(50)"
             "}",
             Settings(
                     queue=FIFO(),
                     autoscaling=Autoscaling(limits=(1, 5)),
                     throttling=TailDropSettings(50)),
             "settings"),

            ("service DB { "
             "  settings {"
             "      queue: LIFO"
             "  }"
             "  operation Select { "
             "      think 4 "
             "  }"
             "}"
             "client Browser { "
             "  every 5 { "
             "      query DB/Select"
             "  }"
             "}",
             Sequence(DefineService("DB", Sequence(Settings(queue=LIFO()), DefineOperation("Select", Think(4)))),
                      DefineClientStub("Browser", 5, Query("DB", "Select"))),
             "unit")

        ]


class ParserErrorTests(ParserTests):

    def test_illegal_expression(self):
        try:
            from mad.parsing import lexer
            text = "qqqquery DB/Select"
            self.file_system.define(self.MAD_FILE, text)
            self._do_parse("query")
            self.fail("Syntax error expected, but no exception was raised.")

        except MADSyntaxError as error:
            self.assertEqual((1, 0), error.position)

