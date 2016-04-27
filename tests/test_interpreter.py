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
from tests.fakes import InMemoryDataStorage

from mad.ast.commons import *
from mad.ast.definitions import *
from mad.ast.actions import *
from mad.simulation.factory import Simulation
from mad.simulation.service import Service, Operation
from mad.evaluation import Symbols, Error
from mad.simulation.requests import Request


class TestInterpreter(TestCase):

    def setUp(self):
        self.simulation = Simulation(InMemoryDataStorage(None))

    def define(self, symbol, value):
        self.simulation.environment.define(symbol, value)
        return value

    def look_up(self, symbol):
        return self.simulation.environment.look_up(symbol)

    def evaluate(self, expression, continuation=lambda x:x):
        return self.simulation.evaluate(expression, continuation)

    def verify_definition(self, symbol, kind):
        value = self.look_up(symbol)
        self.assertTrue(isinstance(value, kind))

    def send_request(self, service_name, operation_name, on_success=lambda:None, on_error=lambda:None):
        service = self.look_up(service_name)
        request = self.fake_request(operation_name, on_success=on_success, on_error=on_error)
        request.send_to(service)
        return request

    def simulate_until(self, end):
        self.simulation.run_until(end)

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
        self.simulate_until(10)

        self.assertEqual(db.process.call_count, 1)

    def test_query_make_services_busy(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Think(2)
                )
            )
        ).value
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("show",
                     Query("DB", "Select")
                )
            )
        ).value

        request = self.send_request("Front-end", "show")
        self.simulate_until(1)
        self.assertEqual(100.0, front_end.utilisation) # The front-end should be busy

        self.simulate_until(2)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released
        self.assertEqual(0.0, db.utilisation) # DB has not yet received the request

        self.simulate_until(3)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released
        self.assertEqual(100.0, db.utilisation) # DB busy thinking

        self.simulate_until(5)
        self.assertEqual(0.0, front_end.utilisation) # Front end has nothing to do
        self.assertEqual(100.0, db.utilisation) # DB busy sending answer

        self.simulate_until(6)
        self.assertEqual(0.0, front_end.utilisation) # Front end has nothing to do
        self.assertEqual(0.0, db.utilisation) # DB has nothing to do anymore

        self.simulate_until(7)
        self.assertEqual(100.0, front_end.utilisation) # Front end busy replying
        self.assertEqual(0.0, db.utilisation) # DB has nothing to do anymore

        self.simulate_until(8)
        self.assertEqual(0.0, front_end.utilisation) # Front end busy replying
        self.assertEqual(0.0, db.utilisation) # DB has nothing to do anymore

        self.simulate_until(9)
        self.assertTrue(request.status == request.OK)

    def test_trigger_make_services_busy(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Think(2)
                )
            )
        ).value
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("show",
                     Trigger("DB", "Select")
                )
            )
        ).value

        request = self.send_request("Front-end", "show")
        self.simulate_until(1)
        self.assertEqual(100.0, front_end.utilisation) # The front-end should be busy
        self.assertEqual(0.0, db.utilisation) # DB has nothing to do

        self.simulate_until(2)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released
        self.assertEqual(0.0, db.utilisation) # DB has not yet received the request

        self.simulate_until(3)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released
        self.assertEqual(100.0, db.utilisation) # DB busy thinking

        self.simulate_until(4)
        self.assertEqual(100.0, front_end.utilisation) # Front end has received the acceptance ack and is replying
        self.assertEqual(100.0, db.utilisation) # DB busy sending answer

        self.simulate_until(5)
        self.assertEqual(0.0, front_end.utilisation) # Front end has nothing to do
        self.assertEqual(0.0, db.utilisation) # DB has nothing to do anymore

        self.simulate_until(6)
        self.assertTrue(request.status == request.OK)

    def test_rejected_query_make_services_busy(self):
        db = self._a_service_that_rejects_requests()
        self.define("DB", db)
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("show",
                     Query("DB", "Select")
                )
            )
        ).value

        request = self.send_request("Front-end", "show")

        self.simulate_until(1)
        self.assertEqual(100.0, front_end.utilisation) # The front-end should be busy

        self.simulate_until(2)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(3)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(4)
        self.assertEqual(100.0, front_end.utilisation) # Front end has received the acceptance ack and is replying

        self.simulate_until(5)
        self.assertEqual(0.0, front_end.utilisation) # Front end has nothing to do

        self.simulate_until(6)
        self.assertTrue(request.status == request.ERROR)

    def test_failed_query_make_services_busy(self):
        db = self._a_service_that_accepts_but_fails(after=3)
        self.define("DB", db)
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("show",
                     Query("DB", "Select")
                )
            )
        ).value

        request = self.send_request("Front-end", "show")

        self.simulate_until(1)
        self.assertEqual(100.0, front_end.utilisation) # The front-end should be busy

        self.simulate_until(2)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(3)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(7)
        self.assertEqual(100.0, front_end.utilisation) # Front-end forward the error

        self.simulate_until(8)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(9)
        self.assertTrue(request.status == request.ERROR)

    def test_rejected_trigger_make_services_busy(self):
        db = self._a_service_that_rejects_requests()
        self.define("DB", db)
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("show",
                     Trigger("DB", "Select")
                )
            )
        ).value

        request = self.send_request("Front-end", "show")

        self.simulate_until(1)
        self.assertEqual(100.0, front_end.utilisation) # The front-end should be busy

        self.simulate_until(2)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(3)
        self.assertEqual(0.0, front_end.utilisation) # The front-end should be released

        self.simulate_until(4)
        self.assertEqual(100.0, front_end.utilisation) # Front end has received the acceptance ack and is replying

        self.simulate_until(5)
        self.assertEqual(0.0, front_end.utilisation) # Front end has nothing to do

        self.simulate_until(6)
        self.assertTrue(request.status == request.ERROR)


    def test_evaluate_timeout_queries(self):
        db = self.define("DB", self._a_service_that_replies_after(8))
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                     Query("DB", "op", timeout=5)
                )
            )
        ).value

        request = self.send_request("Front-end", "checkout")
        self.simulate_until(50)

        self.assertEqual(Request.ERROR, request.status)
        self.assertEqual(0, front_end.tasks.blocked_count)

    def test_evaluate_timeout_no_expiration(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("op", Think(1))
            )
        ).value
        front_end = self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                     Retry(expression=Query("DB", "op", timeout=1),
                           delay=Delay(2, "constant"),
                           limit=5)
                )
            )
        ).value

        request = self.send_request("Front-end", "checkout")
        self.simulate_until(25)

        self.assertEqual(Request.ERROR, request.status)

    def test_sequence_evaluation(self):
        db = self.define("DB", self._a_service_that_accepts_but_fails(after=2))
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

    def test_retry_and_succeed(self):
        db = self.define("DB", self.service_that_succeeds_at_attempt(2))
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Retry(Query("DB", "insert"), limit=5, delay=Delay(10, "constant"))
                )
            )
        )

        def test_fail():
            self.fail("Expected failed request")

        self.send_request("Front-end", "checkout", on_error=test_fail)
        self.simulate_until(200)

        self.assertEqual(db.process.call_count, 2)

    def test_retry_and_fail(self):
        db = self.define("DB", self.service_that_succeeds_at_attempt(15))
        self.evaluate(
            DefineService("Front-end",
                DefineOperation("checkout",
                    Retry(Query("DB", "insert"), limit=5, delay=Delay(10, "constant"))
                )
            )
        )

        def test_fail():
            self.fail("Expected successful request")

        self.send_request("Front-end", "checkout", on_success=test_fail)
        self.simulate_until(200)

        self.assertEqual(db.process.call_count, 5)

    def test_fail(self):
        self.evaluate(
            DefineService("DB",
                DefineOperation("Select", Fail())
            )
        )

        def test_failed():
            self.fail("Expected successful request")

        self.send_request("DB", "Select", on_success=test_failed)
        self.simulate_until(20)

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
        self.simulate_until(10)

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
        self.simulate_until(10)

        self.assertEqual(fake_service.process.call_count, 1)

    def test_client_stub_definition(self):
        client = self.evaluate(
            Sequence(
                DefineService(
                    "Service X",
                    DefineOperation("op", Think(2))
                ),
                DefineClientStub(
                    "Client", 10,
                    Query("Service X", "op"))
            )
        ).value
        client.on_success = MagicMock()

        self.simulate_until(26)

        self.assertEqual(client.on_success.call_count, 2)

    def fake_request(self, operation, on_success=lambda: None, on_error=lambda: None):
        return Request(self.fake_client(), Request.QUERY, operation, 1, on_success=on_success, on_error=on_error)

    def fake_service(self):
        fake_service = MagicMock()
        fake_service.process = MagicMock()
        fake_service.schedule = self.simulation.schedule
        return fake_service

    def fake_client(self):
        fake_client = MagicMock()
        fake_client.schedule = self.simulation.schedule
        fake_client.next_request_id = MagicMock(side_effect = range(1, 100))
        return fake_client

    def _a_service_that_rejects_requests(self):
        def always_reject(request):
            request.reject()
        service = self.fake_service()
        service.process.side_effect = always_reject
        return service

    def _a_service_that_accepts_but_fails(self, after=4):
        def always_accept(request):
            def do_fail():
                request.reply_error()

            request.accept()
            self.simulation._scheduler.after(after, do_fail)

        service = self.fake_service()
        service.process.side_effect = always_accept
        return service

    def _a_service_that_replies_after(self, after=4):
        def always_accept(request):
            def do_succeed():
                request.reply_success()

            request.accept()
            self.simulation._scheduler.after(after, do_succeed)

        service = self.fake_service()
        service.process.side_effect = always_accept
        return service

    def service_that_always_fails(self):
        def always_fail(request):
            request.reply_error()

        service = self.fake_service()
        service.process.side_effect = always_fail
        return service

    def service_that_succeeds_at_attempt(self, successful_attempt):
        attempt = 0

        def respond(request):
            nonlocal attempt
            attempt += 1
            if attempt == successful_attempt:
                request.reply_success()
            else:
                request.reply_error()

        service = self.fake_service()
        service.process.side_effect = respond
        service.schedule = self.simulation.schedule
        return service



