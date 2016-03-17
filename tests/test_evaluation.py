

from unittest import TestCase

from mad.environment import Environment
from mad.ast import Settings
from mad.simulation import Evaluation, Symbols, LIFOTaskPool


class EvaluationTest(TestCase):

   def test_evaluation_of_settings(self):
        settings = Settings(queue=Settings.Queue.LIFO)

        environment = Environment()
        Evaluation(environment, settings).result

        queue = environment.look_up(Symbols.QUEUE)
        self.assertIsInstance(queue, LIFOTaskPool)
