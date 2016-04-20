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
from mad.evaluation import Symbols
from mad.simulation.factory import Factory
from mad.simulation.monitoring import Monitor, Probe, Statistics
from mad.simulation.events import Dispatcher


FAKE_REQUEST = "whatever"


class StatisticsTests(TestCase):

    def setUp(self):
        self.statistics = Statistics()

    def test_rejection_count(self):
        expected_count = 3
        for i in range(expected_count):
            self.statistics.rejection_of(FAKE_REQUEST)

        self.assertEqual(expected_count, self.statistics.rejection_count)

    def test_request_count(self):
        expected_count = 10
        for i in range(expected_count):
            self.statistics.arrival_of(FAKE_REQUEST)

        self.assertEqual(expected_count, self.statistics.request_count)

    def test_reset(self):
        self.statistics.arrival_of(FAKE_REQUEST)
        self.statistics.rejection_of(FAKE_REQUEST)
        self.statistics.error_replied_to(FAKE_REQUEST)
        self.statistics.reset()

        self.assertEqual(0, self.statistics.request_count)
        self.assertEqual(0, self.statistics.rejection_count)
        self.assertEqual(0, self.statistics.error_response_count)

    def test_error_response(self):
        self.statistics.error_replied_to(FAKE_REQUEST)

        self.assertEqual(1, self.statistics.error_response_count)

    def test_reliability(self):
        self.statistics.arrival_of(FAKE_REQUEST)
        self.statistics.arrival_of(FAKE_REQUEST)
        self.statistics.arrival_of(FAKE_REQUEST)
        self.statistics.arrival_of(FAKE_REQUEST)
        self.statistics.rejection_of(FAKE_REQUEST)
        self.statistics.error_replied_to(FAKE_REQUEST)

        expected = (4 - 1 - 1) / 4

        self.assertEqual(expected, self.statistics.reliability)


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

    def test_runs_with_the_proper_period(self):
        with patch.object(Monitor, 'monitor') as monitor:
            period = 50
            monitor = self._create_monitor(period)

            test_duration = 200
            self.simulation.run_until(test_duration)

            expected_call_count = int(test_duration / period)
            self.assertEqual(expected_call_count, monitor.monitor.call_count)

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

