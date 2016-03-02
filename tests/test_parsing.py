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


from unittest import TestCase, main
from mad.parsing import Parser


class ParsingTests(TestCase):


    def setUp(self):
        self.parser = Parser()


    def test_parsing_architecture(self):
        text = "architecture SensApp:" \
               "    service Foo:" \
               "        operation Bar:" \
               "            request Baz/Quz { timeout: 15 }"
        architecture = self.parser.parse(text)
        self.assertEqual("SensApp", architecture.name)


    def test_parsing_service(self):
        text = "service Dispatcher:" \
               "    operation op1:" \
               "        trigger Foo/Bar" \
               "    operation op2:" \
               "        trigger Foo/Quz"

        service = self.parser.parse(text, entry_rule="service")

        self.assertEqual("Dispatcher", service.name)
        self.assertEqual(2, len(service.operations))


    def test_parsing_service_with_configuration(self):
        text = "service Dummy:" \
               "    configuration:" \
               "        queue: FIFO" \
               "    operation foo:" \
               "        trigger YYY/XXX"

        service = self.parser.parse(text, entry_rule="service")

        self.assertEqual("Dummy", service.name)


    def test_parsing_configuration(self):
        text = "configuration: " \
               "    queue: LIFO" \
               "    resources: shared" \
               "    throttling: CoDel" \
               "    autoscaling: rules(utilisation, 40, 60, 1)"

        configuration = self.parser.parse(text, entry_rule="configuration")

        self.assertEqual(4, len(configuration))


    def test_parsing_lifo_queue(self):
        self.verify_setting("queue: LIFO", "queue", "LIFO")

    def test_parsing_queue(self):
        self.verify_setting("queue: FIFO", "queue", "FIFO")

    def test_parsing_resources(self):
        self.verify_setting("resources: shared", "resources", "shared")

    def test_parsing_throttling(self):
        self.verify_setting("throttling: taildrop", "throttling", "taildrop")

    def test_parsing_red_throttling(self):
        self.verify_setting("throttling: RED", "throttling", "RED")

    def test_parsing_throttling(self):
        self.verify_setting("throttling: CoDel", "throttling", "CoDel")

    def verify_setting(self, text, entry_rule, expectation):
        (_, value) = self.parser.parse(text, entry_rule)
        self.assertEqual(expectation, value)


    def test_parsing_autoscaling(self):
        text = "autoscaling: rules(utilisation, 40, 60, 1)"

        scaling = self.parser.parse(text, "autoscaling")

        self.assertEqual(40, scaling.lower_edge)
        self.assertEqual(60, scaling.upper_edge)
        self.assertEqual(1, scaling.magnitude)


    def test_parsing_operation(self):
        text = "operation BigHairyOperation:" \
               "    trigger ServiceA/op1" \
               "    request ServiceB/op2"

        operation = self.parser.parse(text, entry_rule="operation")

        self.assertEqual("BigHairyOperation", operation.name)
        self.assertEqual(2, len(operation.behaviour))

    def test_parsing_request_action(self):
        text = "request ServiceX/operationY"

        action = self.parser.parse(text, entry_rule="request")

        self.assertEqual("ServiceX", action.service)
        self.assertEqual("operationY", action.operation)

    def test_parsing_action_with_options(self):
        text = "request ServiceX/OperationY {timeout: 20}"

        action = self.parser.parse(text, entry_rule="action")

        self.assertEqual(20, action.timeout)

    def test_parsing_timeout(self):
        text = "timeout: 123"

        (key, timeout) = self.parser.parse(text, entry_rule="timeout")

        self.assertEqual("timeout", key)
        self.assertEqual(123, timeout)

    def test_parsing_on_error(self):
        text = "on-error: fail"

        (key, on_error) = self.parser.parse(text, entry_rule="on_error")

        self.assertEqual("on-error", key)
        self.assertEqual("FAIL", on_error)

    def test_parsing_on_error_with_retry(self):
        text = "on-error: retry(limit: 5, delay: 10)"

        (key, retry) = self.parser.parse(text, entry_rule="on_error")

        self.assertEqual("on-error", key)
        self.assertEqual(5, retry.limit)
        self.assertEqual(10, retry.delay)


if __name__ == "__main__":
    main()