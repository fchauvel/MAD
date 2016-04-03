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

from mad.simulation.tasks import LIFOTaskPool, FIFOTaskPool


class LIFOTaskPoolTests(TestCase):

    def test_take(self):
        pool = LIFOTaskPool()

        pool.put("request 1")
        pool.put("request 2")
        pool.put("request 3")

        self.assertEqual("request 3", pool.take())

    def test_take_fails_when_empty(self):
        pool = LIFOTaskPool()
        self.assertTrue(pool.is_empty)

        with self.assertRaises(ValueError):
            pool.take()

    def test_reactivated_task_are_taken_first(self):
        pool = LIFOTaskPool()

        pool.put("request 1")
        pool.put("request 2")
        pool.activate("request 3")
        pool.put("request 4")

        # FIXME: It is not clear which request should come first? The third or the four?
        self.assertEqual("request 4", pool.take())


class TaskPoolTests(TestCase):

    def test_put_increases_size(self):
        pool = self._create_pool()
        pool.put("request 1")

        self.assertEqual(pool.size, 1)

    def _create_pool(self):
        return FIFOTaskPool()

    def test_take_decreases_size(self):
        pool = self._create_pool()
        pool.put("request 1")
        pool.put("request 2")

        pool.take()

        self.assertEqual(pool.size, 1)

    def test_taking_from_empty_pool_fails(self):
        pool = self._create_pool()
        with self.assertRaises(ValueError):
            pool.take()

    def test_activate_increases_size(self):
        pool = self._create_pool()
        pool.activate("request")
        self.assertEqual(pool.size, 1)

    def test_activated_requests_come_out_first(self):
        pool = self._create_pool()
        pool.put("task 1")
        pool.activate("task 2")
        pool.put("task 3")

        self.assertEqual(pool.take(), "task 2")


if __name__ == "__main__":
    import unittest.main
    unittest.main()