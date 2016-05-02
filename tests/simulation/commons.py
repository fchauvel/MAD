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
from mad.simulation.requests import Request


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

    def send_request(self, kind, service_name, operation_name, on_success=lambda:None, on_error=lambda:None):
        service = self.look_up(service_name)
        request = self.fake_request(kind, operation_name, on_success=on_success, on_error=on_error)
        request.send_to(service)
        return request

    def query(self, service, operation, on_success=lambda:None, on_error=lambda:None):
        return self.send_request(Request.QUERY, service, operation,on_success=on_success, on_error=on_error)

    def trigger(self, service, operation, on_success=lambda:None, on_error=lambda:None):
        return self.send_request(Request.TRIGGER, service, operation,on_success=on_success, on_error=on_error)

    def fake_request(self, kind, operation, on_success=lambda: None, on_error=lambda: None):
        return Request(self.fake_client(), kind, operation, 1, on_success=on_success, on_error=on_error)

    def fake_client(self):
        fake_client = MagicMock()
        fake_client.schedule = self.simulation.schedule
        fake_client.next_request_id = MagicMock(side_effect=range(1, 1000))
        return fake_client