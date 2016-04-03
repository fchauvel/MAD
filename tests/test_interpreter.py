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

from mock import MagicMock, call

from mad.ast import *
from mad.datasource import InMemoryDataSource
from mad.datasource import Project
from mad.simulation.factory import Simulation
from mad.simulation.autoscaling import AutoScaler
from mad.simulation.service import Service, Operation
from mad.evaluation import Symbols
from mad.log import InMemoryLog
from mad.monitoring import CSVReportFactory
from mad.simulation.autoscaling import AutoScalingStrategy
from mad.simulation.requests import Request

class TestInterpreter(TestCase):

    def setUp(self):
        factory = CSVReportFactory(Project("test.mad", 25), InMemoryDataSource())
        self.simulation = Simulation(log=InMemoryLog(), report_factory=factory)

    def define(self, symbol, value):
        self.simulation.environment.define(symbol, value)
        return value

    def look_up(self, symbol):
        return self.simulation.environment.look_up(symbol)

    def evaluate(self, expression):
        return self.simulation.evaluate(expression)

    def verify_definition(self, symbol, kind):
        value = self.look_up(symbol)
        self.assertTrue(isinstance(value, kind))

    def send_request(self, service_name, operation_name):
        service = self.look_up(service_name)
        request = self.fake_request(operation_name)
        request.send_to(service)

    def simulate_until(self, end):
        self.simulation.run_until(end)

    def test_evaluate_non_blocking_service_invocation(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.define(Symbols.SELF, self.fake_client())
        self.evaluate(Trigger("serviceX", "op"))

        self.assertEqual(fake_service.process.call_count, 1)

    def test_evaluate_blocking_service_invocation(self):
        db = self.define("DB", self.fake_service())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                     Query("DB", "op")
                )
            )
        )

        self.send_request("Front-end", "checkout")

        self.assertEqual(db.process.call_count, 1)

    def test_sequence_evaluation(self):
        db = self.define("DB", self.service_that_always_fails())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Sequence(
                        Trigger("DB", "op"),
                        Trigger("DB", "op")
                    )
                )
            )
        )

        self.send_request("Front-end", "checkout")
        self.simulate_until(20)

        self.assertEqual(db.process.call_count, 2)

    def test_operation_invocation(self):
        # TODO: Check whether this test is still useful
        db = self.define("DB", self.service_that_always_fails())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Trigger("DB", "op")
                )
            )
        )

        self.send_request("Front-end", "checkout")
        self.simulate_until(20)

        self.assertEqual(db.process.call_count, 1)

    def test_thinking(self):
        db = self.define("DB", self.service_that_always_fails())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Sequence(
                        Think(5),
                        Trigger("DB", "op")
                    )
                )
            )
        )

        self.send_request("Front-end", "checkout")

        self.assertEqual(db.process.call_count, 0)
        self.simulate_until(10)
        self.assertEqual(db.process.call_count, 1)

    def test_retry_on_error(self):
        db = self.define("DB", self.service_that_always_fails())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Retry(Query("DB", "insert"), 4)
                )
            )
        )

        self.send_request("Front-end", "checkout")
        self.simulate_until(20)

        self.assertEqual(db.process.call_count, 4)

    def test_ignore_error(self):
        db1 = self.define("DB1", self.service_that_always_fails())
        db2 = self.define("DB2", self.fake_service())
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Sequence(
                        IgnoreError(Query("DB1", "op")),
                        Trigger("DB2", "op")
                    )
                )
            )
        )

        self.send_request("Front-end", "checkout")
        self.simulate_until(20)

        self.assertEqual(db1.process.call_count, 1)
        self.assertEqual(db2.process.call_count, 1)

    def test_operation_definition(self):
        self.evaluate(DefineOperation("op", Trigger("serviceX", "op")))

        self.verify_definition("op", Operation)

    def test_service_request(self):
        fake_service = self.define("serviceX", self.fake_service())
        service = self.evaluate(
            DefineService("my-service",
                DefineOperation(
                    "op",
                    Trigger("serviceX", "op")
                )
            )
        ).value

        request = self.fake_request("op")
        request.send_to(service)

        self.assertEqual(fake_service.process.call_count, 1)

    def test_service_definition(self):
        fake_service = self.define("service Y", self.fake_service())
        self.evaluate(
                DefineService(
                    "Service X",
                    DefineOperation("op", Trigger("service Y", "foo"))
                )
        )

        self.verify_definition("Service X", Service)
        service = self.look_up("Service X")

        request = self.fake_request("op")
        request.send_to(service)

        self.assertEqual(fake_service.process.call_count, 1)

    def test_client_stub_definition(self):
        client = self.evaluate(
            Sequence(
                DefineService(
                    "Service X",
                    DefineOperation("op", Think(2))
                ),
                DefineClientStub(
                    "Client", 5,
                    Query("Service X", "op"))
            )
        ).value
        client.on_success = MagicMock()

        self.simulate_until(20 + 2)

        self.assertEqual(client.on_success.call_count, 4)

    def test_autoscaler(self):
        fake_service = MagicMock(Service)
        self.define(Symbols.SERVICE, fake_service)

        strategy = MagicMock(AutoScalingStrategy)

        autoscaler = AutoScaler(self.simulation.environment, 10, strategy)
        self.define(Symbols.AUTOSCALING, autoscaler)

        self.simulate_until(20)

        expected_calls = [call(fake_service), call(fake_service)]
        strategy.adjust.assert_has_calls(expected_calls)

    def fake_request(self, operation):
        return Request(self.fake_client(), operation)

    def fake_service(self):
        fake_service = MagicMock()
        fake_service.process = MagicMock()
        return fake_service

    def fake_client(self):
        fake_client = MagicMock()
        return fake_client

    def service_that_always_fails(self):
        def always_fail(request):
            request.reply_error()

        service = self.fake_service()
        service.process.side_effect = always_fail
        return service




