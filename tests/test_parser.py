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

from mad.ast import *
from mock import MagicMock

from mad.parsing import Parser, Source


class ParserTests(TestCase):

    def test_parsing_all_expressions(self):
        for (text, expected_result, rule) in self._all_expressions():
            actual_result = self._do_parse(text, rule)
            self.assertEqual(expected_result, actual_result, "Fail to parse '%s'" % text)

    def _all_expressions(self):
        return [
            ("query DB/Select", Query("DB", "Select"), "query"),
            ("invoke DB/Select", Trigger("DB", "Select"), "invoke"),
            ("think 5", Think(5), "think"),
            ("think 5 invoke DB/Select", Sequence(Think(5), Trigger("DB", "Select")), "action_list"),

            ("operation Select: think 5",
             DefineOperation("Select", Think(5)),
             "define_operation"),

            ("service DB: operation Select: think 4", DefineService("DB", DefineOperation("Select", Think(4))), "define_service"),

            ("client Browser: every 5: query DB/Select", DefineClientStub("Browser", 5, Query("DB", "Select")), "define_client"),

            ("settings: queue: LIFO", Settings(queue=LIFO()), "settings"),

            ("service DB: "
             "  operation Select: "
             "      think 4 "
             "client Browser: "
             "  every 5: "
             "      query DB/Select",
             Sequence(DefineService("DB", DefineOperation("Select", Think(4))),
                      DefineClientStub("Browser", 5, Query("DB", "Select"))),
             "unit"),

            ("autoscaling:"
             "  period: 10"
             "  limits: [1, 5]",
             {"autoscaling": Autoscaling(period=10, limits=(1, 5))},
             "autoscaling"),

            ("settings:"
             "  queue: FIFO"
             "  autoscaling:"
             "      limits: [1, 5]",
             Settings(queue=FIFO(), autoscaling=Autoscaling(limits=(1, 5))),
             "settings"),

            ("service DB: "
             "  settings:"
             "      queue: LIFO"
             "  operation Select: "
             "      think 4 "
             "client Browser: "
             "  every 5: "
             "      query DB/Select",
             Sequence(DefineService("DB", Sequence(Settings(queue=LIFO()), DefineOperation("Select", Think(4)))),
                      DefineClientStub("Browser", 5, Query("DB", "Select"))),
             "unit")

        ]

    def _do_parse(self, text, rule):
        source = self._make_source("test.mad", text)
        parser = Parser(source)
        return parser.parse("test.mad", entry_rule=rule, logger=None)

    def _make_source(self, name, text):
        source = MagicMock(Source)
        source.read = MagicMock()
        source.read.return_value = text
        return source