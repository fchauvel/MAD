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

from mad.des2.environment import Environment
from mad.des2.simulation import Simulator, Simulation, Service, Operation, Request
from mad.des2.ast import *


class TestSimulation(TestCase):

    def setUp(self):
        self.environment = Environment()
        self.simulation = Simulation(self.environment)

    def define(self, symbol, value):
        self.environment.define(symbol, value)
        return value

    def look_up(self, symbol):
        return self.environment.look_up(symbol)

    def evaluate(self, expression):
        return self.simulation.evaluate(expression)

    def verify_definition(self, symbol, kind):
        value = self.environment.look_up(symbol)
        self.assertTrue(isinstance(value, kind))

    def test_service_invocation_evaluation(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.simulation.evaluate(Trigger("serviceX", "op"))

        self.assertEqual(fake_service.process.call_count, 1)

    def test_sequence_evaluation(self):
        fake_service = self.define("serviceX", self.fake_service())

        self.simulation.evaluate(Sequence(Trigger("serviceX", "op"), Trigger("serviceX", "op")))

        self.assertEqual(fake_service.process.call_count, 2)

    def test_operation_invocation(self):
        fake_service = self.define("serviceX", self.fake_service())
        operation = self.define("op-foo", Operation([],
                                                    Trigger("serviceX", "op"),
                                                    self.environment))

        operation.invoke([])

        self.assertEqual(fake_service.process.call_count, 1)

    def test_operation_definition(self):
        self.evaluate(DefineOperation("op", Trigger("serviceX", "op")))

        self.verify_definition("op", Operation)

    def test_service_request(self):
        env = self.environment.create_local_environment()
        fake_service = self.define("serviceX", self.fake_service())
        service = self.define("my-service", Service(env))
        env.define("op", Operation([],
                                   Trigger("serviceX", "op"),
                                   self.environment))

        service.process(Request("op"))

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

        service.process(Request("op"))

        self.assertEqual(fake_service.process.call_count, 1)

    def fake_service(self):
        fake_service = MagicMock()
        fake_service.process = MagicMock()
        return fake_service