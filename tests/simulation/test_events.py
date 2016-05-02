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
from mock import MagicMock, call, ANY

from tests.simulation.commons import ServiceTests

from mad.evaluation import Symbols
from mad.ast.definitions import *
from mad.ast.actions import *
from mad.simulation.events import Listener, Dispatcher
from mad.simulation.throttling import ThrottlingWrapper, ThrottlingPolicyDecorator
from mad.simulation.requests import Request

FAKE_REQUEST = "whatever"
FAKE_SERVICE = "service"


class DispatcherTests(TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher()

    def test_register_rejects_non_listener(self):
        with self.assertRaises(AssertionError):
            self.dispatcher.register("this is not a listener")

    def test_notifies_only_once_despite_multiple_registration(self):
        listener = self._fake_listener()
        self.dispatcher.register(listener)
        self.dispatcher.register(listener)

        self.dispatcher.task_created(FAKE_REQUEST)

        listener.task_created.assert_called_once_with(FAKE_REQUEST)

    def test_dispatch(self):
        invocations = [
            ("task_created", [FAKE_REQUEST]),
            ("task_rejected", [FAKE_REQUEST]),
            ("task_failed", [FAKE_REQUEST]),
            ("task_successful", [FAKE_REQUEST]),
            ("posting_of", [FAKE_SERVICE, FAKE_REQUEST]),
            ("acceptance_of", [FAKE_REQUEST]),
            ("rejection_of", [FAKE_REQUEST]),
            ("success_of", [FAKE_REQUEST]),
            ("failure_of", [FAKE_REQUEST]),
            ("timeout_of", [FAKE_REQUEST]),
            ("task_ready", [FAKE_REQUEST]),
            ("task_running", [FAKE_REQUEST]),
            ("resuming", [FAKE_REQUEST])
        ]

        for (method_name, parameters) in invocations:
            self._do_test_dispatch_of(method_name, *parameters)

    def _do_test_dispatch_of(self, method_name, *parameters):
        listener = self._fake_listener()

        method = getattr(self.dispatcher, method_name)
        method(*parameters)

        delegate = getattr(listener, method_name)
        delegate.assert_called_once_with(*parameters)

    def _fake_listener(self):
        listener = MagicMock(Listener)
        self.dispatcher.register(listener)
        return listener


class NotificationTests(ServiceTests):

    def test_server_notifies_rejection(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Think(5)
                )
            )
        ).value

        fake_task_pool = MagicMock(ThrottlingPolicyDecorator)
        fake_task_pool._accepts = MagicMock(return_value=False)
        db.tasks = ThrottlingWrapper(db.environment, task_pool=fake_task_pool)

        listener = MagicMock(Listener)
        db.environment.look_up(Symbols.LISTENER).register(listener)

        request1 = self.query("DB", "Select")
        request2 = self.query("DB", "Select")
        self.simulate_until(10)

        expected_calls = [
            call.task_created(request1),
            call.task_created(request2),
            call.task_rejected(request2),
            call.task_successful(request1)]

        self.assertEqual(expected_calls, listener.method_calls, listener.method_calls)

    def test_client_notifies_rejection_on_trigger(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("insert",
                     Think(5)
                )
            )
        ).value
        storage = self.evaluate(
            DefineService("Storage",
                DefineOperation("store",
                     Trigger("DB", "insert")
                )
            )
        ).value

        fake_task_pool = MagicMock(ThrottlingPolicyDecorator)
        fake_task_pool._accepts = MagicMock(return_value=False)
        db.tasks = ThrottlingWrapper(db.environment, task_pool=fake_task_pool)
        db.workers.busy_workers.extend(db.workers.idle_workers)
        db.workers.idle_workers = []

        listener = MagicMock(Listener)
        storage.environment.look_up(Symbols.LISTENER).register(listener)

        request = self.trigger("Storage", "store")
        self.simulate_until(10)

        expected_calls = [
            call.task_created(request),
            call.posting_of("DB", ANY),
            call.rejection_of(ANY),
            call.task_failed(request)
        ]

        self.assertEqual(request.status, Request.ERROR)
        self.assertTrue(listener.method_calls == expected_calls, listener.method_calls)

    def test_notifies_arrival_and_success(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Think(5)
                )
            )
        ).value

        listener = MagicMock(Listener)
        db.environment.look_up(Symbols.LISTENER).register(listener)

        request = self.query("DB", "Select")
        self.simulate_until(10)

        expected_calls = [
            call.task_created(request),
            call.task_successful(request)]

        self.assertEqual(expected_calls, listener.method_calls, listener.method_calls)

    def test_notifies_arrival_and_failure(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Fail()
                )
            )
        ).value

        listener = MagicMock(Listener)
        db.environment.look_up(Symbols.LISTENER).register(listener)

        request = self.query("DB", "Select")
        self.simulate_until(10)

        expected_calls = [
            call.task_created(request),
            call.task_failed(request)]

        self.assertEqual(expected_calls, listener.method_calls, listener.method_calls)

    def test_notifies_when_request_timeout(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Fail()
                )
            )
        ).value

        listener = MagicMock(Listener)
        db.environment.look_up(Symbols.LISTENER).register(listener)

        request = self.query("DB", "Select")
        request.reply_error()
        self.simulate_until(40)

        expected_calls = [
            call.task_created(request),
            call.task_failed(request)]

        self.assertEqual(expected_calls, listener.method_calls, listener.method_calls)

    def test_task_status_notification(self):
        db = self.evaluate(
            DefineService("DB",
                DefineOperation("Select",
                     Think(5)
                )
            )
        ).value

        listener = MagicMock(Listener)
        db.environment.look_up(Symbols.LISTENER).register(listener)

        query_1 = self.query("DB", "Select")
        query_2 = self.query("DB", "Select")
        self.simulate_until(15)

        expected_calls = [
            call.task_created(query_1),
            call.task_created(query_2),
            call.task_ready(query_2),
            call.task_successful(query_1),
            call.task_running(query_2),
            call.task_successful(query_2),
        ]

        self.assertEqual(expected_calls, listener.method_calls, listener.method_calls)
