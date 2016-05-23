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

from mad.evaluation import Symbols
from tests.fakes import InMemoryDataStorage, InMemoryFileSystem

from mad.ast.commons import *
from mad.ast.definitions import *
from mad.ast.actions import *
from mad.log import Event
from mad.simulation.factory import Simulation
from mad.simulation.monitoring import Logger

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
        worker_pool = server.environment.look_up(Symbols.WORKER_POOL)
        self.assertEqual(5, worker_pool.capacity)


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
                [Event(5,   "Client",       Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(6,   "Client",       Logger.REQUEST_SENT.format(request=1, service="Server", operation="op")),
                 Event(6,   "Client",       Logger.TASK_PAUSED.format(task=-1)),
                 Event(7,   "Server",       Logger.REQUEST_RECEIVED.format(request=1)),
                 Event(7,   "Server",       Logger.TASK_ASSIGNED.format(task=1, worker=1)),
                 Event(8,   "Client",       Logger.REQUEST_ACCEPTED.format(request=1)),
                 Event(8,   "Server",       Logger.REQUEST_SENT.format(request=2, service="Database", operation="op")),
                 Event(8,   "Server",       Logger.TASK_PAUSED.format(task=1)),
                 Event(9,   "Database",     Logger.REQUEST_RECEIVED.format(request=2)),
                 Event(9,   "Database",     Logger.TASK_ASSIGNED.format(task=2, worker=1)),
                 Event(10,  "Client",       Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(10,  "Server",       Logger.REQUEST_ACCEPTED.format(request=2)),

                 Event(11,  "Client",       Logger.REQUEST_SENT.format(request=3, service="Server", operation="op")),
                 Event(11,  "Client",       Logger.TASK_PAUSED.format(task=-1)),
                 Event(12,  "Server",       Logger.REQUEST_RECEIVED.format(request=3)),
                 Event(12,  "Server",       Logger.TASK_ASSIGNED.format(task=3, worker=1)),
                 Event(13,  "Client",       Logger.REQUEST_ACCEPTED.format(request=3)),
                 Event(13,  "Server",       Logger.REQUEST_SENT.format(request=4, service="Database", operation="op")),
                 Event(13,  "Server",       Logger.TASK_PAUSED.format(task=3)),
                 Event(14,  "Database",     Logger.REQUEST_RECEIVED.format(request=4)),
                 Event(14,  "Database",     Logger.TASK_ACTIVATED.format(task=4)),
                 Event(15,  "Client",       Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(15,  "Server",       Logger.REQUEST_ACCEPTED.format(request=4)),

                 Event(16,  "Client",       Logger.REQUEST_SENT.format(request=5, service="Server", operation="op")),
                 Event(16,  "Client",       Logger.TASK_PAUSED.format(task=-1)),
                 Event(17,  "Server",       Logger.REQUEST_RECEIVED.format(request=5)),
                 Event(17,  "Server",       Logger.TASK_ASSIGNED.format(task=5, worker=1)),
                 Event(18,  "Database",     Logger.SUCCESS_REPLIED.format(request=2)),
                 Event(18,  "Database",     Logger.TASK_ASSIGNED.format(task=4, worker=1)),
                 Event(18,  "Client",       Logger.REQUEST_ACCEPTED.format(request=5)),
                 Event(18,  "Server",       Logger.REQUEST_SENT.format(request=6, service="Database", operation="op")),
                 Event(18,  "Server",       Logger.TASK_PAUSED.format(task=5)),
                 Event(19,  "Server",       Logger.REQUEST_SUCCESS.format(request=2)),
                 Event(19,  "Server",       Logger.TASK_ACTIVATED.format(task=1)),
                 Event(19,  "Server",       Logger.TASK_ASSIGNED.format(task=1, worker=1)),
                 Event(19,  "Database",     Logger.REQUEST_RECEIVED.format(request=6)),
                 Event(19,  "Database",     Logger.TASK_ACTIVATED.format(task=6)),
                 Event(20,  "Client",       Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(20,  "Server",       Logger.SUCCESS_REPLIED.format(request=1)),
                 Event(20,  "Server",       Logger.REQUEST_ACCEPTED.format(request=6))]
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
                [Event(10, "C1", Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(11, "C1", Logger.REQUEST_SENT.format(request=1, service="S1", operation="op")),
                 Event(11, "C1", Logger.TASK_PAUSED.format(task=-1)),
                 Event(12, "S1", Logger.REQUEST_RECEIVED.format(request=1)),
                 Event(12, "S1", Logger.TASK_ASSIGNED.format(task=1, worker=1)),
                 Event(13, "C1", Logger.REQUEST_ACCEPTED.format(request=1)),
                 Event(16, "S1", Logger.SUCCESS_REPLIED.format(request=1)),
                 Event(17, "C1", Logger.REQUEST_SUCCESS.format(request=1)),
                 Event(17, "C1", Logger.TASK_ACTIVATED.format(task=-1)),
                 Event(17, "C1", Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(17, "C1", Logger.SUCCESS_REPLIED.format(request=-1)),
                 Event(20, "C1", Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(21, "C1", Logger.REQUEST_SENT.format(request=2, service="S1", operation="op")),
                 Event(21, "C1", Logger.TASK_PAUSED.format(task=-1)),
                 Event(22, "S1", Logger.REQUEST_RECEIVED.format(request=2)),
                 Event(22, "S1", Logger.TASK_ASSIGNED.format(task=2, worker=1)),
                 Event(23, "C1", Logger.REQUEST_ACCEPTED.format(request=2)),
                 Event(26, "S1", Logger.SUCCESS_REPLIED.format(request=2)),
                 Event(27, "C1", Logger.REQUEST_SUCCESS.format(request=2)),
                 Event(27, "C1", Logger.TASK_ACTIVATED.format(task=-1)),
                 Event(27, "C1", Logger.TASK_ASSIGNED.format(task=-1, worker=-1)),
                 Event(27, "C1", Logger.SUCCESS_REPLIED.format(request=-1)),
                 ]
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