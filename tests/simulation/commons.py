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

from mad.simulation.factory import Simulation
from mad.simulation.requests import Query, Trigger
from mad.simulation.tasks import Task, TaskStatus


class ServiceTests(TestCase):
    """
    Factor out the creation of the simulation, as well as a few helpers needed to create services that do
    reject requests, or services that always fail, etc.
    """

    def setUp(self):
        self.simulation = Simulation(InMemoryDataStorage(None))

    def define(self, symbol, value):
        self.simulation.environment.define(symbol, value)
        return value

    def look_up(self, symbol):
        return self.simulation.environment.look_up(symbol)

    def evaluate(self, expression, continuation=lambda x:x):
        return self.simulation.evaluate(expression, continuation)

    def simulate_until(self, end):
        self.simulation.run_until(end)

    def query(self, service_name, operation, on_success=lambda:None, on_error=lambda:None):
        request = Query(self.a_running_task(), operation, 1, lambda s:None)
        request.on_success = on_success
        request.on_error = on_error
        self.send(request, service_name)
        return request

    def a_running_task(self):
        task = Task(self.fake_client())
        task.status = TaskStatus.BLOCKED # A regular evaluation would block it after sending the request
        return task

    def trigger(self, service_name, operation, on_success=lambda:None, on_error=lambda:None):
        request = Trigger(self.a_running_task(), operation, 1, lambda s:None)
        request.on_success = on_success
        request.on_error = on_error
        self.send(request, service_name)
        return request

    def send(self, request, service_name):
        service_name = self.look_up(service_name)
        request.send_to(service_name)

    def fake_client(self):
        fake_client = MagicMock()
        fake_client.schedule = self.simulation.schedule
        fake_client.next_request_id = MagicMock(side_effect=range(1, 1000))
        return fake_client