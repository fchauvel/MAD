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
from mock import MagicMock, PropertyMock
from tests.fakes import InMemoryDataStorage

from mad.evaluation import Symbols

from mad.simulation.factory import Simulation
from mad.simulation.workers import WorkerPoolWrapper, WorkerPool, Worker
from mad.simulation.autoscaling import AutoScaler, RuleBasedStrategy


class MockFactory:

    def __init__(self):
        self.simulation = Simulation(InMemoryDataStorage(None))

    def worker_pool(self):
        wrapper = MagicMock()
        wrapper.set_capacity = MagicMock()
        wrapper.worker_count = MagicMock(return_value=10)
        wrapper.utilisation = MagicMock(return_value=50.)
        self.simulation.environment.define(Symbols.WORKER_POOL, wrapper)
        return wrapper

    def auto_scaling_strategy(self, adjust_return):
        strategy = MagicMock(RuleBasedStrategy)
        strategy.adjust.return_value = adjust_return
        return strategy


class AutoScalerTest(TestCase):

    def setUp(self):
        self.mock = MockFactory()

    def test_triggers_periodically(self):
        (duration, period) = (20, 10)

        worker_pool = self.mock.worker_pool()
        strategy = self.mock.auto_scaling_strategy(adjust_return=10)
        AutoScaler(self.mock.simulation.environment, 10, (1, 3), strategy)

        self.mock.simulation.run_until(20)

        self.assertEqual(duration / period, strategy.adjust.call_count)

    def test_lower_limit_is_not_exceeded(self):
        (min, max) = (1, 30)
        worker_pool = self.mock.worker_pool()
        strategy = self.mock.auto_scaling_strategy(adjust_return=min-1)
        auto_scaler = AutoScaler(self.mock.simulation.environment, 10, (min, max), strategy)

        auto_scaler.auto_scale()

        worker_pool.set_capacity.assert_called_once_with(min)

    def test_upper_limit_is_not_exceeded(self):
        (min, max) = (1, 30)
        worker_pool = self.mock.worker_pool()
        strategy = self.mock.auto_scaling_strategy(adjust_return=max+1)
        auto_scaler = AutoScaler(self.mock.simulation.environment, 10, (min, max), strategy)

        auto_scaler.auto_scale()

        worker_pool.set_capacity.assert_called_once_with(max)


class AutoScalingTests(TestCase):

    def test_decrease_worker_count(self):
        autoscaling = RuleBasedStrategy(70, 80)
        worker_pool = self.prepare_service(worker_count=5, utilisation=50.)

        actual = autoscaling.adjust(worker_pool)

        self.assertEqual(4, actual)

    def test_increase_when_utilisation_too_high(self):
        autoscaling = RuleBasedStrategy(70, 80)
        worker_pool = self.prepare_service(worker_count=4, utilisation=100.)

        actual = autoscaling.adjust(worker_pool)

        self.assertEqual(5, actual)

    def test_does_not_change_a_value_within_the_range(self):
        worker_count = 4
        autoscaling = RuleBasedStrategy(70, 80)
        service = self.prepare_service(worker_count, utilisation=75.)

        actual = autoscaling.adjust(service)

        self.assertEqual(worker_count, actual)

    def prepare_service(self, worker_count, utilisation):
        import math
        service = MagicMock()
        type(service).utilisation = PropertyMock(return_value=utilisation)
        type(service).capacity = PropertyMock(return_value=worker_count)
        service.set_worker_count = MagicMock()
        return service
