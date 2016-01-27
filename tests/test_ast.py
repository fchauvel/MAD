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
from mad.ast import Architecture, Service, Operation, RequestAction, TriggerAction, UtilisationRule, Retry


class ArchitectureTests(TestCase):

    def test_architecture_have_name(self):
        name = "dummy name"
        archi = Architecture(name)
        self.assertEqual(name, archi.name)

    def test_architecture_reject_missing_name(self):
        with self.assertRaises(ValueError):
            archi = Architecture("")


class ServiceTest(TestCase):

    def test_service_have_name(self):
        name = "dummy"
        service = Service(name, ["whatever"])
        self.assertEqual(name, service.name)

    def test_service_must_have_valid_names(self):
        with self.assertRaises(ValueError):
            Service(None, ["whatever"])

    def test_service_must_have_at_least_one_operation(self):
        with self.assertRaises(ValueError):
            Service("dummy name", [])


class OperationTest(TestCase):

    def test_operations_have_name(self):
        name = "dummy"
        operation = Operation(name,["whatever"])
        self.assertEqual(name, operation.name)

    def test_invalid_names_are_rejected(self):
        with self.assertRaises(ValueError):
            Operation(None, ["whatever"])

    def test_operations_have_behaviour(self):
        behaviour = ["blablabla"]
        operation = Operation("dummy", behaviour)
        self.assertEqual(1, len(operation.behaviour))

    def test_invalid_behaviours_are_rejected(self):
        with self.assertRaises(ValueError):
            Operation("dummy", [])


class TestAction:

    def create_action(self, service, operation, timeout=10):
        pass

    def test_actions_refer_to_an_operation(self):
        service = "service X"
        operation = "operation A"

        trigger = self.create_action(service, operation)

        self.assertEqual(service, trigger.service)
        self.assertEqual(operation, trigger.operation)

    def test_invalid_operation_are_rejected(self):
        with self.assertRaises(ValueError):
            self.create_action("dummy", None)

    def test_invalid_service_are_rejected(self):
        with self.assertRaises(ValueError):
            self.create_action(None, "dummy operation")

    def test_has_timeout(self):
        action = self.create_action("Svc", "Op.", timeout=1234)
        self.assertEqual(1234, action.timeout)

    def test_negative_timeout_are_rejected(self):
        with self.assertRaises(ValueError):
            action = self.create_action("Svc", "Op", timeout=-34)


class TestTriggerAction(TestAction, TestCase):

    def create_action(self, service, operation, timeout=10):
        return TriggerAction(service, operation, timeout)


class TestRequestAction(TestAction, TestCase):

    def create_action(self, service, operation, timeout=10):
        return RequestAction(service, operation, timeout)


class TestUtilisationRules(TestCase):

    def test_has_lower_edge(self):
        rule = UtilisationRule(75, 85, 1)

        self.assertEqual(75, rule.lower_edge)
        self.assertEqual(85, rule.upper_edge)
        self.assertEqual(1, rule.magnitude)


class TestRetry(TestCase):

    def test_retry_has_limit(self):
        retry = Retry(15)
        self.assertEqual(15, retry.limit)

    def test_retry_has_no_negative_limit(self):
        with self.assertRaises(ValueError):
            Retry(-15)

    def test_retry_has_delay(self):
        retry = Retry(15, 10)
        self.assertEqual(10, retry.delay)


if __name__ == "__main__":
    import unittest.main as main
    main()