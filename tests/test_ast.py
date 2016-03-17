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

from mad.ast import *
from mad.simulation import Evaluation


class ThinkTest(TestCase):

    def test_equality(self):
        exp1 = Think(5)
        exp2 = Think(6)
        exp3 = Think(5)

        self.assertNotEqual(exp1, exp2)
        self.assertEqual(exp1, exp3)


class QueryTests(TestCase):

    def test_equality(self):
        queries = [ Query("S1", "Op1"),
                    Query("S1", "Op2"),
                    Query("S2", "Op1"),
                    Query("S2", "Op2"),
                    Query("S1", "Op1")]

        self.assertNotEqual(queries[0], queries[1])
        self.assertNotEqual(queries[0], queries[2])
        self.assertNotEqual(queries[0], queries[3])
        self.assertEqual(queries[0], queries[4])


class SequenceTests(TestCase):

    def test_equality(self):
        seq1 = Sequence(Think(5), Think(6))
        seq2 = Sequence(Think(5), Think(6))

        self.assertEqual(seq1, seq2)


class SettingsTest(TestCase):

    def test_default_queue_settings_is_fifo(self):
        settings = Settings()
        self.assertEqual(Settings.Queue.FIFO, settings.queue)

    def test_setting_queue(self):
        settings = Settings(queue=Settings.Queue.LIFO)
        self.assertEqual(Settings.Queue.LIFO, settings.queue)

    def test_accept(self):
        settings = Settings()
        evaluation = MagicMock(Evaluation)
        settings.accept(evaluation)

        evaluation.of_settings.assert_called_once_with(settings)
