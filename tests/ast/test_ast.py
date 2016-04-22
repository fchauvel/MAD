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

from mad.ast.commons import *
from mad.ast.actions import *


class ExpressionTest(TestCase):

    def test_concatenation(self):
        actual = Think(1) + Think(2)
        self.assertEqual(Sequence(Think(1), Think(2)), actual)

    def test_concatenation_with_sequence(self):
        actual = Think(1) + Sequence(Think(2), Think(3))
        self.assertEqual(Sequence(Think(1), Think(2), Think(3)), actual)


class RetryTests(TestCase):

    def test_defaults(self):
        retry = Retry(Think(5))

        self.assertIsNone(retry.limit)
        self.assertIs(Retry.DEFAULT_DELAY, retry.delay)

    def test_expose_limit(self):
        limit = 10
        retry = Retry(Think(5), limit=limit)
        self.assertEqual(limit, retry.limit)

    def test_expose_delay(self):
        delay = Delay(10, "exponential")
        retry = Retry(Think(5), delay=delay)

        self.assertIs(delay, retry.delay)


class FailTests(TestCase):

    def test_default_probability(self):
        fail = Fail()
        self.assertEqual(1., fail.probability)

    def test_rejects_negative_probability(self):
        with self.assertRaises(AssertionError):
            Fail(-23)

    def test_evaluation(self):
        evaluation = MagicMock()
        evaluation.of_fail = MagicMock()
        fail = Fail(0.5)
        fail.accept(evaluation)

        evaluation.of_fail.assert_called_once_with(fail)


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

    def test_setting_priority(self):
        desired_priority = 17
        invocation = Query("DB", "Select", desired_priority)
        self.assertEqual(desired_priority, invocation.priority)

    def test_default_priority(self):
        invocation = Query("DB", "Select")
        self.assertEqual(Invocation.DEFAULT_PRIORITY, invocation.priority)

    def test_default_timeout(self):
        invocation = Query("DB", "Select")
        self.assertFalse(invocation.has_timeout)

    def test_setting_timeout(self):
        desired_timeout = 25
        invocation = Query("DB", "Select", timeout=desired_timeout)
        self.assertTrue(invocation.has_timeout)
        self.assertEqual(desired_timeout, invocation.timeout)


class TriggerTests(TestCase):

    def test_setting_priority(self):
        desired_priority = 17
        invocation = Trigger("DB", "Select", desired_priority)
        self.assertEqual(desired_priority, invocation.priority)

    def test_default_priority(self):
        invocation = Trigger("DB", "Select")
        self.assertEqual(Invocation.DEFAULT_PRIORITY, invocation.priority)


class SequenceTests(TestCase):

    def test_equality(self):
        seq1 = Sequence(Think(5), Think(6))
        seq2 = Sequence(Think(5), Think(6))

        self.assertEqual(seq1, seq2)

    def test_concatenation_between_sequence(self):
        seq1 = Sequence(Think(1), Think(2))
        seq2 = Sequence(Think(3), Think(4))

        actual = seq1 + seq2
        expected = Sequence(Think(1), Think(2), Think(3), Think(4))
        self.assertEqual(expected, actual)

    def test_concatenation_with_an_expression(self):
        seq = Sequence(Think(1), Think(2))

        actual = seq + Think(3)

        expected = Sequence(Think(1), Think(2), Think(3))
        self.assertEqual(expected, actual)


