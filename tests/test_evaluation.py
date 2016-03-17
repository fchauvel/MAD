

from unittest import TestCase

from mad.environment import Environment
from mad.ast import *
from mad.simulation import Evaluation, Symbols, LIFOTaskPool, FIFOTaskPool


class EvaluationTest(TestCase):

    def test_evaluation_of_fifo(self):
        environment = Environment()
        queue = FIFO()

        Evaluation(environment, queue).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, FIFOTaskPool)

    def test_evaluation_of_lifo(self):
        environment = Environment()
        queue = LIFO()

        Evaluation(environment, queue).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, LIFOTaskPool)

    def test_evaluation_of_settings(self):
        settings = Settings(queue=LIFO())

        environment = Environment()
        Evaluation(environment, settings).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, LIFOTaskPool)
