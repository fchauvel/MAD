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

from mad.environment import Environment
from mad.ast.settings import *
from mad.log import InMemoryLog
from mad.monitoring import ReportFactory
from mad.evaluation import Evaluation, Symbols
from mad.simulation.factory import Simulation, Factory
from mad.simulation.tasks import LIFOTaskPool, FIFOTaskPool
from mad.simulation.autoscaling import AutoScaler


class EvaluationTest(TestCase):

    def test_evaluation_of_fifo(self):
        environment = Environment()
        queue = FIFO()

        Evaluation(environment, queue, Factory()).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, FIFOTaskPool)

    def test_evaluation_of_lifo(self):
        environment = Environment()
        queue = LIFO()

        Evaluation(environment, queue, Factory()).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, LIFOTaskPool)

    def test_evaluation_of_queue_settings(self):
        settings = Settings(queue=LIFO())

        simulation = Simulation(InMemoryLog(), MagicMock(ReportFactory))
        simulation.evaluate(settings)

        queue = simulation.environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, LIFOTaskPool)

    def test_evaluation_of_autoscaling_settings(self):
        PERIOD = 23
        settings = Settings(autoscaling=Autoscaling(PERIOD, limits=(3, 5)))

        simulation = Simulation(InMemoryLog(), MagicMock(ReportFactory))
        simulation.evaluate(settings)

        autoscaler = simulation.environment.look_up(Symbols.AUTOSCALING)
        self.assertIsInstance(autoscaler, AutoScaler)
        self.assertEqual(PERIOD, autoscaler.period)



