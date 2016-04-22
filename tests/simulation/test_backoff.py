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
from mock import patch

from mad.simulation.backoff import ConstantBackoff, ExponentialBackoff

BASE_DELAY = 25


class ConstantDelayTests(TestCase):

    def test_constant_delay(self):
        backoff = ConstantBackoff(BASE_DELAY)

        for attempts in range(10):
            self.assertEqual(backoff.delay(attempts), BASE_DELAY)


def fake_pick_up_to(limit):
    return limit


class ExponentialBackoffTests(TestCase):


    TEST_CASES = [
        {"attempts": 0, "expected_delay": 0},
        {"attempts": 1, "expected_delay": BASE_DELAY},
        {"attempts": 4, "expected_delay": BASE_DELAY * fake_pick_up_to(2**4-1)}
    ]

    def setUp(self):
        self.backoff = ExponentialBackoff(BASE_DELAY)

    @patch.object(ExponentialBackoff, "_pick_up_to", side_effect=fake_pick_up_to)
    def test_delay(self, mock):
        for each_case in self.TEST_CASES:
            self._do_test_delay(**each_case)

    def _do_test_delay(self, attempts, expected_delay):
        delay = self.backoff.delay(attempts)

        self.assertEqual(expected_delay, delay,
                         "Error! delay({0:d}) = {1:d} (found {2:d})".format(attempts, expected_delay, delay))

    def test_pick_up_to(self):
        limit = BASE_DELAY * (2 ** 5 - 1)
        for i in range(100):
            delay = self.backoff.delay(5)
            self.assertGreaterEqual(limit, delay)
