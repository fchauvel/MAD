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

from mad.queueing import FIFO, LIFO


class TestFIFO(TestCase):

    def make_queue(self, content):
        return FIFO(content)

    def test_queue_is_empty_by_default(self):
        queue = self.make_queue([])
        self.assertTrue(queue.is_empty)

    def test_put(self):
        queue = self.make_queue([])
        queue.put(2)
        self.assertEqual(1, queue.length)

    def test_cannot_take_from_empty_queue(self):
        queue = self.make_queue([])
        with self.assertRaises(ValueError):
            queue.take()

    def test_take(self):
        queue = self.make_queue([1,2,3,4,5,6])
        old_length = queue.length
        self.assertEqual(1, queue.take())
        self.assertEqual(old_length - 1, queue.length)

    def test_length(self):
        queue = self.make_queue([1,2,3,4])
        self.assertEqual(4, queue.length)


class TestLIFO(TestFIFO):

    def make_queue(self, content):
        return LIFO(content)

    def test_take(self):
        queue = self.make_queue([1,2,3,4,5,6])
        old_length = queue.length
        self.assertEqual(6, queue.take())
        self.assertEqual(old_length - 1, queue.length)
