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


from unittest import TestCase, main

from mad.simulation.workers import WorkerPool


class WorkerPoolTests(TestCase):

    def test_all_busy(self):
        pool = WorkerPool(["a", "b", "c"])
        self.assertTrue(pool.are_available)
        for i in range(3):
            pool.acquire_one()
        self.assertFalse(pool.are_available)

    def test_acquiring_idle_worker(self):
        pool = WorkerPool(["a", "b", "c"])
        pool.acquire_one()
        self.assertEqual(pool.idle_worker_count, 2)

    def test_release_worker(self):
        pool = WorkerPool(["a", "b", "c"])
        pool.acquire_one()
        pool.release("d")
        self.assertEqual(pool.idle_worker_count, 3)

    def test_acquire_is_not_permitted_on_empty_pools(self):
        pool = WorkerPool(["w1"])
        pool.acquire_one()
        with self.assertRaises(ValueError):
            pool.acquire_one()

    def test_utilisation(self):
        pool = WorkerPool(["w1", "w2", "w3", "w4"])
        self.assertAlmostEqual(pool.utilisation, float(0))
        pool.acquire_one()
        pool.acquire_one()
        self.assertAlmostEqual(pool.utilisation, float(100 * 2 / 4))
        pool.add_workers(["w5", "w6"])
        self.assertAlmostEqual(pool.utilisation, float(100 * 2 / 6))
        pool.release("w2")
        self.assertAlmostEqual(pool.utilisation, float(100 * 1 / 6))
        pool.shutdown(4)
        self.assertAlmostEqual(pool.utilisation, float(100 * 1 / 2))


    def test_add_worker(self):
        pool = WorkerPool(["w1", "w2"])
        self.assertEqual(2, pool.capacity)

        pool.add_workers(["w3", "w4"])
        self.assertEqual(4, pool.capacity)


if __name__ == "__main__":
    import unittest.main
    unittest.main()