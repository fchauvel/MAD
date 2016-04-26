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
from mock import MagicMock, patch

from tests.fakes import InMemoryDataStorage

from mad.log import Log
from mad.evaluation import Symbols
from mad.simulation.factory import Factory
from mad.simulation.monitoring import OperationStatistics, Monitor, Probe, Statistics, Logger
from mad.simulation.events import Dispatcher
from mad.simulation.requests import Request


def _a_fake_request(operation="foo", response_time=5):
    request = MagicMock()
    type(request).operation = operation
    type(request).response_time = response_time
    return request


class OperationStatisticsTests(TestCase):

    def setUp(self):
        self.operation = OperationStatistics()

    def test_call_count(self):
        for i in range(3):
            self.operation.call()

        self.assertEqual(3, self.operation.call_count)

    def test_rejection_count(self):
        for i in range(5):
            self.operation.call_rejected()

        self.assertEqual(5, self.operation.rejection_count)

    def test_reliability(self):
        self.assertIsNone(self.operation.reliability)

        for i in range(10):
            self.operation.call_succeed(4)
        for i in range(5):
            self.operation.call_failed()
        for i in range(2):
            self.operation.call_rejected()

        expectation = 10 / (10 + 5 + 2)
        self.assertEqual(expectation, self.operation.reliability)

    def test_response_time(self):
        self.assertIsNone(self.operation.response_time)

        durations = [4, 5, 6, 7, 8]
        for each_duration in durations:
            self.operation.call_succeed(each_duration)

        expectation = sum(durations) / len(durations)
        self.assertEqual(expectation, self.operation.response_time)

    def test_reset(self):
        self.operation.call()
        self.operation.call_failed()
        self.operation.call()
        self.operation.call_succeed(56)
        self.operation.reset()

        self.assertIsNone(self.operation.reliability)
        self.assertIsNone(self.operation.response_time)
        self.assertEqual(0, self.operation.call_count)
        self.assertEqual(0, self.operation.success_count)


class StatisticsTests(TestCase):

    def setUp(self):
        self.statistics = Statistics()

    def test_rejection_count(self):
        expected_count = 3
        for i in range(expected_count):
            self.statistics.rejection_of(_a_fake_request())

        self.assertEqual(expected_count, self.statistics.rejection_count)

    def test_request_count(self):
        expected_count = 10
        for i in range(expected_count):
            self.statistics.arrival_of(_a_fake_request())

        self.assertEqual(expected_count, self.statistics.arrival_count)

    def test_reset(self):
        self.statistics.arrival_of(_a_fake_request())
        self.statistics.rejection_of(_a_fake_request())
        self.statistics.error_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request(10))
        self.statistics.reset()

        self.assertEqual(0, self.statistics.arrival_count)
        self.assertEqual(0, self.statistics.rejection_count)
        self.assertEqual(0, self.statistics.failure_count)
        self.assertIsNone(self.statistics.response_time)

    def test_error_response(self):
        self.statistics.error_replied_to(_a_fake_request())

        self.assertEqual(1, self.statistics.failure_count)

    def test_success_count(self):
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.rejection_of(_a_fake_request())
        self.statistics.error_replied_to(_a_fake_request())

        self.assertEqual(4, self.statistics.success_count)

    def test_reliability(self):
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.success_replied_to(_a_fake_request())
        self.statistics.rejection_of(_a_fake_request())
        self.statistics.error_replied_to(_a_fake_request())

        expected = 4 / (4+2)

        self.assertEqual(expected, self.statistics.reliability)

    def test_response_time(self):
        response_times = [10, 6, 7, 9, 8]
        self._success_of_requests(response_times)

        expectation = sum(response_times) / len(response_times)
        self.assertEqual(expectation, self.statistics.response_time)

    def test_response_time_per_operation(self):
        requests = [{"operation": "foo", "response_time": 12},
                    {"operation": "foo", "response_time": 14},
                    {"operation": "bar", "response_time": 5},
                    {"operation": "bar", "response_time": 3},
                    {"operation": "quz", "response_time": 10}]

        for each_request in requests:
            request = _a_fake_request(**each_request)
            self.statistics.success_replied_to(request)

        self.assertEqual(13.0, self.statistics.response_time_for("foo"))
        self.assertEqual(4.0, self.statistics.response_time_for("bar"))
        self.assertEqual(10, self.statistics.response_time_for("quz"))

    def _success_of_requests(self, response_times=[3,4,5,6]):
        for each_response_time in response_times:
            request = _a_fake_request(response_time=each_response_time)
            self.statistics.success_replied_to(request)



class ProbeTests(TestCase):

    def test_formatted(self):
        probe = Probe("text", 5, "{:d}", lambda x: 5)

        text = probe.formatted(None)

        self.assertEqual("    5", text)

    def test_formatted_floating(self):
        probe = Probe("text", 5, "{:5.2f}", lambda x: 5.34)

        text = probe.formatted(None)

        self.assertEqual(" 5.34", text)

    def test_missing_value(self):
        probe = Probe("text", 5, "{:5.2f}", lambda x: None)

        text = probe.formatted(None)

        self.assertEqual("   NA", text)


class MonitorTests(TestCase):

    def setUp(self):
        self.factory = Factory()
        self.storage = InMemoryDataStorage(None)
        self.simulation = self.factory.create_simulation(self.storage)

    def test_throughput_calculation(self):
        period = 10
        self.monitor = self._create_monitor(period)

        (success, rejection, error) = (10, 3, 4)
        self._run_scenario(success, rejection, error)

        expected = (success) / period
        self.assertEqual(expected, self.monitor._throughput())

    def _run_scenario(self, total, rejected, errors):
        for i in range(total):
            self.monitor.statistics.success_replied_to(_a_fake_request())
        for i in range(rejected):
            self.monitor.statistics.rejection_of(_a_fake_request())
        for i in range(errors):
            self.monitor.statistics.error_replied_to(_a_fake_request())

    def test_runs_with_the_proper_period(self):
        with patch.object(Monitor, 'monitor') as trigger:
            period = 50
            self._create_monitor(period)

            test_duration = 200
            self.simulation.run_until(test_duration)

            expected_call_count = int(test_duration / period)
            self.assertEqual(expected_call_count, trigger.call_count)

    def test_setting_probes(self):
        fake_report = MagicMock()
        self.storage.report_for = MagicMock(return_value=fake_report)
        monitor = self._create_monitor()
        monitor.set_probes([Probe("time", 5, "{:d}", lambda self: 10),
                            Probe("weather", 10, "{:s}", lambda self: "cloudy")])

        monitor.monitor()

        fake_report.assert_called_once_with(time="   10", weather="    cloudy")

    def _create_monitor(self, period=50):
        environment = self.simulation.environment.create_local_environment()
        environment.define(Symbols.LISTENER, Dispatcher())
        self._create_fake_service(environment)
        monitor = Monitor(Symbols.MONITOR, environment, period)
        self.simulation.environment.define(Symbols.MONITOR, monitor)
        return monitor

    def _create_fake_service(self, environment):
        fake_service = MagicMock()
        fake_service.name = "Bidon"
        environment.define(Symbols.SERVICE, fake_service)


class LoggerTest(TestCase):
    CALLER = "Client"
    CALLEE = "DB"
    OPERATION = "Select"
    REQUEST_ID = 123

    def setUp(self):
        self.factory = Factory()
        self.storage = InMemoryDataStorage(None)
        self.storage._log = MagicMock(Log)
        self.simulation = self.factory.create_simulation(self.storage)
        service = MagicMock()
        service.name = self.CALLER
        self.simulation.environment.define(Symbols.SELF, service)
        self.simulation.environment.define(Symbols.LISTENER, MagicMock(Dispatcher))
        self.logger = Logger(self.simulation.environment)

    def test_logging_request_arrival(self):
        self.logger.arrival_of(self._fake_request())
        self.verify_log_call(Logger.REQUEST_ARRIVAL % self.REQUEST_ID)

    def test_logging_request_stored(self):
        self.logger.storage_of(self._fake_request())
        self.verify_log_call(Logger.REQUEST_STORED % self.REQUEST_ID)

    def test_logging_failure_of(self):
        self.logger.failure_of(self._fake_request())
        self.verify_log_call(Logger.REQUEST_FAILURE % self.REQUEST_ID)

    def test_logging_success_of(self):
        self.logger.success_of(self._fake_request())
        self.verify_log_call(Logger.REQUEST_SUCCESS % self.REQUEST_ID)

    def test_logging_posting_of(self):
        self.logger.posting_of(self.CALLEE, self._fake_request())
        self.verify_log_call(Logger.REQUEST_SENT % (self.REQUEST_ID, self.CALLEE, self.OPERATION))

    def test_logging_timeout_of(self):
        self.logger.timeout_of(self._fake_request())
        self.verify_log_call(Logger.REQUEST_TIMEOUT % self.REQUEST_ID)

    def test_logging_error_replied(self):
        self.logger.error_replied_to(self._fake_request())
        self.verify_log_call(Logger.ERROR_REPLIED % self.REQUEST_ID)

    def test_logging_success_replied(self):
        self.logger.success_replied_to(self._fake_request())
        self.verify_log_call(Logger.SUCCESS_REPLIED % self.REQUEST_ID)

    def verify_log_call(self, message):
        self.simulation.log.record.assert_called_once_with(0, self.CALLER, message)

    def _fake_request(self):
        request = MagicMock(Request)
        request.identifier = self.REQUEST_ID
        request.operation = self.OPERATION
        return request