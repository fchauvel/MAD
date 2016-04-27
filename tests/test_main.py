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

from io import StringIO

from unittest import TestCase, skip
from tests.fakes import InMemoryDataStorage, InMemoryFileSystem

from mad.ast.commons import *
from mad.ast.definitions import *
from mad.ast.actions import *
from mad.log import Event
from mad.simulation.factory import Simulation

from mad.ui import Controller


class TestXXX(TestCase):
    # TODO to be move in the acceptance tests

    def setUp(self):
        self.file_system = InMemoryFileSystem()

    @skip("Debugging Sensapp example")
    def test_sensapp(self):
        with open("C:/Users/franckc/home/projects/diversify/dev/mad/samples/sensapp/sensapp.mad") as source:
            self.file_system.define("test.mad", source.read())

        controller = Controller(StringIO(), self.file_system)
        simulation = controller.execute("test.mad", "200")

    def test_client_server_with_autoscaling(self):
        self.file_system.define(
            "test.mad",
            "service DB {"
            "   settings {"
            "      autoscaling {"
            "          period: 10"
            "          limits: [3, 6]"
            "      }"
            "   }"
            "   operation Select {"
            "      think 9"
            "   }"
            "}"
            "client Browser {"
            "  every 2 {"
            "      query DB/Select"
            "  }"
            "}")

        controller = Controller(StringIO(), self.file_system)
        simulation = controller.execute("test.mad", "115")

        server = simulation.environment.look_up("DB")
        self.assertEqual(5, server.worker_count)


class TestMain(TestCase):

    def setUp(self):
        self.parser = None

    #@skip
    def test_worker_do_not_wait_for_response(self):

        expression = Sequence(
            DefineService(
                "Database",
                DefineOperation("op", Think(8))),
            DefineService(
                "Server",
                DefineOperation("op", Query("Database", "op"))),
            DefineClientStub(
                "Client",
                5,
                Query("Server", "op"))
        )

        simulation = self.evaluate(expression)
        self.run_until(simulation, 20)

        self.verify_trace(
                simulation,
                [Event(6,   "Client",       "Sending Req. 1 to Server::op"),
                 Event(7,   "Server",       "Req. 1 accepted"),
                 Event(8,   "Server",       "Sending Req. 2 to Database::op"),
                 Event(9,   "Database",     "Req. 2 accepted"),

                 Event(11,  "Client",       "Sending Req. 3 to Server::op"),
                 Event(12,  "Server",       "Req. 3 accepted"),
                 Event(13,  "Server",       "Sending Req. 4 to Database::op"),
                 Event(14,  "Database",     "Req. 4 accepted"),
                 Event(14,  "Database",     "Req. 4 enqueued"),

                 Event(16,  "Client",       "Sending Req. 5 to Server::op"),
                 Event(17,  "Server",       "Req. 5 accepted"),
                 Event(18,  "Database",     "Reply to Req. 2 (SUCCESS)"),
                 Event(18,  "Server",       "Sending Req. 6 to Database::op"),
                 Event(19,  "Server",       "Req. 2 complete"),
                 Event(19,  "Database",     "Req. 6 accepted"),
                 Event(19,  "Database",     "Req. 6 enqueued"),
                 Event(20,  "Server",       "Reply to Req. 1 (SUCCESS)")]
            )


    def test_simple_example(self):
        model = "service S1:" \
                "   operation op: " \
                "      think 5" \
                "" \
                "client C1:" \
                "   every 10:" \
                "       query S1::op"

        expression = Sequence(
            DefineService(
                "S1",
                DefineOperation(
                        "op",
                        Think(3))),
            DefineClientStub(
                "C1",
                10,
                Query("S1", "op")
            )
        )
        simulation = self.evaluate(expression)
        self.run_until(simulation, 27)

        self.verify_trace(
                simulation,
                [Event(11, "C1", "Sending Req. 1 to S1::op"),
                 Event(12, "S1", "Req. 1 accepted"),
                 Event(16, "S1", "Reply to Req. 1 (SUCCESS)"),
                 Event(17, "C1", "Req. 1 complete"),
                 Event(21, "C1", "Sending Req. 2 to S1::op"),
                 Event(22, "S1", "Req. 2 accepted"),
                 Event(26, "S1", "Reply to Req. 2 (SUCCESS)"),
                 Event(27, "C1", "Req. 2 complete")]
        )

    def evaluate(self, expression):
        simulation = Simulation(InMemoryDataStorage(None))
        simulation.evaluate(expression)
        return simulation

    def run_until(self, simulation, limit):
        simulation.run_until(limit)

    def verify_trace(self, simulation, expected_trace):
        actual_trace = simulation.log
        self.assertEqual(
                len(actual_trace),
                len(expected_trace),
                "Traces should have the same length (expected %d, found %d)\n%s" % (len(expected_trace), len(actual_trace), str(actual_trace)))
        for (expected, actual) in zip(expected_trace, actual_trace):
            self.verify_event(expected, actual)

    def verify_event(self, expected, actual):
        self.assertEqual(
                expected.time,
                actual.time,
                "Time mismatch (expected time is %d)\n%s" % (expected.time, str(actual)))
        self.assertEqual(
                expected.message,
                actual.message,
                "Message mismatch (expected message is '%s')\n%s" % (expected.message, str(actual)))
        self.assertEqual(
                expected.context,
                actual.context,
                "Context mismatch (expected context is %s)\n%s" % (expected.context, str(actual)))


if __name__ == "__main__":
    import unittest.main as main
    main()