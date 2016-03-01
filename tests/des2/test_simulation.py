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

from mad.des2.simulation import WorkerPool, RequestPool


class RequestPoolTests(TestCase):

    def test_put_increases_size(self):
        pool = RequestPool()
        pool.put("request 1")

        self.assertEqual(pool.size, 1)

    def test_take_decreases_size(self):
        pool = RequestPool()
        pool.put("request 1")
        pool.put("request 2")

        pool.take()

        self.assertEqual(pool.size, 1)

    def test_taking_from_empty_pool_fails(self):
        pool = RequestPool()
        with self.assertRaises(ValueError):
            pool.take()


class WorkerPoolTests(TestCase):

    def test_put_increases_size(self):
        pool = WorkerPool()
        pool.put("new-worker")
        self.assertEqual(pool.size, 1)

    def test_take_decreases_size(self):
        pool = WorkerPool()
        pool.put("worker_1")
        pool.put("worker_2")

        pool.take()

        self.assertEqual(pool.size, 1)

    def test_is_empty(self):
        pool = WorkerPool()
        self.assertTrue(pool.is_empty)

        pool.put("worker_1")
        self.assertFalse(pool.is_empty)

    def test_take_is_not_permitted_on_empty_pools(self):
        pool = WorkerPool()
        with self.assertRaises(ValueError):
            pool.take()



if __name__ == "__main__":
    import unittest.main
    unittest.main()