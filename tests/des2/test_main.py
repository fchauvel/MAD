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

from unittest import TestCase, skip


from mad.des2.ast import *
from mad.des2.environment import GlobalEnvironment
from mad.des2.simulation import Evaluation
from mad.des2.log import Event


class TestMain(TestCase):

    def setUp(self):
        self.parser = None

    @skip
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
        self.run_until(simulation, 13)

        self.verify_trace(
                simulation,
                [Event(5,   "Client",       "Sending Req. 1 to Server::op"),
                 Event(5,   "Server",       "Req. 1 accepted"),
                 Event(5,   "Server",       "Sending Req. 2 to Database::op"),
                 Event(5,   "Database",     "Req. 2 accepted"),
                 Event(10,  "Client",       "Sending Req. 3 to Server::op"),
                 Event(10,  "Server",       "Req. 3 accepted"),
                 Event(10,  "Server",       "Sending Req. 4 to Database::op"),
                 Event(10,  "Database",     "Req. 4 enqueued"),
                 Event(13,  "Database",     "Reply to Req. 2 (SUCCESS)"),
                 Event(13,  "Server",       "Req. 2 complete"),
                 Event(13,  "Server",       "Reply to Req. 1 (SUCCESS)"),
                 Event(13,  "Client",       "Req. 1 complete"),]
        )


    def test_simple_example(self):
        model = "service S1:" \
                "   operation op: " \
                "      think 5" \
                "" \
                "client C1:" \
                "   every 10:" \
                "       query S1::op"

        expression = self.parse(model)
        simulation = self.evaluate(expression)
        self.run_until(simulation, 25)

        self.verify_trace(
                simulation,
                [Event(10, "C1", "Sending Req. 1 to S1::op"),
                 Event(10, "S1", "Req. 1 accepted"),
                 Event(15, "S1", "Reply to Req. 1 (SUCCESS)"),
                 Event(15, "C1", "Req. 1 complete"),
                 Event(20, "C1", "Sending Req. 2 to S1::op"),
                 Event(20, "S1", "Req. 2 accepted"),
                 Event(25, "S1", "Reply to Req. 2 (SUCCESS)"),
                 Event(25, "C1", "Req. 2 complete")]
        )

    def parse(self, model):
        return Sequence(
            DefineService(
                "S1",
                DefineOperation(
                        "op",
                        Think(5))),
            DefineClientStub(
                "C1",
                10,
                Query("S1", "op")
            )
        )

    def evaluate(self, expression):
        simulation = GlobalEnvironment()
        Evaluation(simulation, expression).result
        return simulation

    def run_until(self, simulation, limit):
        simulation.schedule().simulate_until(limit)

    def verify_trace(self, simulation, expected_trace):
        actual_trace = simulation.log()
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
                expected.context,
                actual.context,
                "Context mismatch (expected context is %s)\n%s" % (expected.context, str(actual)))
        self.assertEqual(
                expected.message,
                actual.message,
                "Message mismatch (expected message is '%s')\n%s" % (expected.message, str(actual)))


if __name__ == "__main__":
    import unittest.main as main
    main()