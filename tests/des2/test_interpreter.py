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
from mock import MagicMock

from mad.des2.environment import GlobalEnvironment
from mad.des2.simulation import Evaluation, Service, Operation, Request, Symbols, Error
from mad.des2.ast import *


class TestInterpreter(TestCase):

    def setUp(self):
        self.environment = GlobalEnvironment()

    def define(self, symbol, value):
        self.environment.define(symbol, value)
        return value

    def look_up(self, symbol):
        return self.environment.look_up(symbol)

    def evaluate(self, expression):
        return Evaluation(self.environment, expression).result

    def verify_definition(self, symbol, kind):
        value = self.environment.look_up(symbol)
        self.assertTrue(isinstance(value, kind))

    def simulate_until(self, end):
        self.environment.schedule().simulate_until(end)

    def test_evaluate_non_blocking_service_invocation(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.define(Symbols.SELF, self.fake_client())
        self.evaluate(Trigger("serviceX", "op"))

        self.assertEqual(fake_service.process.call_count, 1)

    def test_evaluate_blocking_service_invocation(self):
        fake_service = self.define("foo", self.fake_service())

        self.define(Symbols.SELF, self.fake_client())
        self.evaluate(Query("foo", "op"))

        self.assertEqual(fake_service.process.call_count, 1)

    def test_sequence_evaluation(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.define(Symbols.SELF, self.fake_client())
        self.evaluate(Sequence(Trigger("serviceX", "op"), Trigger("serviceX", "op")))

        self.assertEqual(fake_service.process.call_count, 2)

    def test_operation_invocation(self):
        fake_service = self.define("serviceX", self.fake_service())
        self.define(Symbols.SELF, self.fake_client())
        operation = self.define("op-foo", Operation("op-foo",
                                                    [],
                                                    Trigger("serviceX", "op"),
                                                    self.environment))

        operation.invoke(self.fake_request("op-foo"), [])

        self.assertEqual(fake_service.process.call_count, 1)

    def test_thinking(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.define(Symbols.SELF, self.fake_client())
        operation = self.define(
                "op-foo",
                Operation(
                        "op-foo",
                        [],
                        Sequence(
                            Think(5),
                            Trigger("serviceX", "op")
                        ),
                        self.environment))

        operation.invoke(self.fake_request("op-foo"), [])

        self.assertEqual(fake_service.process.call_count, 0)

        self.simulate_until(10)

        self.assertEqual(fake_service.process.call_count, 1)

    def test_retry_on_error(self):
        service = self.define("serviceX", self.service_that_always_fails())
        self.define(Symbols.SELF, self.fake_client())

        result = self.evaluate(Retry(Query("serviceX", "op"), 4))

        self.assertEqual(service.process.call_count, 4)
        self.assertFalse(result.is_successful)

    def test_retry_on_error(self):
        service_1 = self.define("service_1", self.service_that_always_fails())
        service_2 = self.define("service_2", self.fake_service())
        self.define(Symbols.SELF, self.fake_client())

        result = self.evaluate(
                Sequence(
                    IgnoreError(Query("service_1", "op")),
                    Trigger("service_2", "op"),
                )
        )

        self.assertEqual(service_1.process.call_count, 1)
        self.assertEqual(service_2.process.call_count, 1)

    def test_operation_definition(self):
        self.evaluate(DefineOperation("op", Trigger("serviceX", "op")))

        self.verify_definition("op", Operation)

    def test_service_request(self):
        fake_service = self.define("serviceX", self.fake_service())
        service = self.evaluate(
            DefineService(
                "my-service",
                DefineOperation(
                    "op",
                    Trigger("serviceX", "op")
                ))).value

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
        client = self.evaluate(DefineClientStub("Client", 5, Query("Service X", "op"))).value
        client.on_success = MagicMock()
        self.evaluate(
                DefineService(
                    "Service X",
                    DefineOperation("op", Think(2))
                )
        )

        self.simulate_until(20 + 2)

        self.assertEqual(client.on_success.call_count, 4)

    def fake_request(self, operation):
        return Request(self.fake_client(), operation, MagicMock(), MagicMock())

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


