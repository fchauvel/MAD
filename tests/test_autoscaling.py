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

from mad.simulation import Service
from mad.autoscaling import AutoScalingStrategy


class AutoScalingTests(TestCase):

    def test_decrease_worker_count(self):
        autoscaling = AutoScalingStrategy(1, 5, 70, 80)
        service = self.prepare_service(worker_count=5, utilisation=50.)

        autoscaling.adjust(service)

        service.set_worker_count.assert_called_once_with(4)

    def test_increase_when_utilisation_too_high(self):
        autoscaling = AutoScalingStrategy(1, 5, 70, 80)
        service = self.prepare_service(worker_count=5, utilisation=99.)

        autoscaling.adjust(service)

        service.set_worker_count.assert_called_once_with(5)

    def test_do_not_decrease_below_minimum(self):
        autoscaling = AutoScalingStrategy(1, 5, 70, 80)
        service = self.prepare_service(worker_count=1, utilisation=50.)

        autoscaling.adjust(service)

        service.set_worker_count.assert_called_once_with(1)

    def test_do_not_exceed_capacity(self):
        autoscaling = AutoScalingStrategy(1, 5, 70, 80)
        service = self.prepare_service(worker_count=5, utilisation=99.)

        autoscaling.adjust(service)

        service.set_worker_count.assert_called_once_with(5)

    def prepare_service(self, worker_count, utilisation):
        service = MagicMock(Service)
        type(service).utilisation = PropertyMock(return_value=utilisation)
        type(service).worker_count = PropertyMock(return_value=worker_count)
        service.set_worker_count = MagicMock()
        return service
