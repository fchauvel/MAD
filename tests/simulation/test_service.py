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

from mad.ast.definitions import DefineOperation
from mad.ast.actions import Think

from mad.evaluation import Symbols
from mad.monitoring import ReportFactory
from mad.log import InMemoryLog

from mad.simulation.factory import Factory
from mad.simulation.requests import Request
from mad.simulation.tasks import TaskPool
from mad.simulation.throttling import ThrottlingPolicy


class ServiceTests(TestCase):

    def test_throttling_is_trigger(self):
        factory = Factory()
        simulation = factory.create_simulation(InMemoryLog(), MagicMock(ReportFactory))

        environment = simulation.environment.create_local_environment()

        throttling = MagicMock(ThrottlingPolicy)
        throttling.accepts.return_value = False
        environment.define(Symbols.THROTTLING, throttling)

        noop = factory.create_operation(environment, DefineOperation("NOOP", Think(5)))
        environment.define("NOOP", noop)

        queue = MagicMock(TaskPool)
        environment.define(Symbols.QUEUE, queue)

        service = factory.create_service("ServiceUnderTest", environment)
        service.workers.acquire_one()

        request = MagicMock(Request)
        request.identifier = 1
        request.operation = "NOOP"
        service.process(request)

        self.assertEquals(1, throttling.accepts.call_count)
        self.assertEquals(0, request.reply_success.call_count)
        self.assertEquals(1, request.reply_error.call_count)

