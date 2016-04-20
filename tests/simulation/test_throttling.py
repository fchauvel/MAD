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
from mock import MagicMock, PropertyMock

from mad.simulation.tasks import TaskPool
from mad.simulation.throttling import NoThrottling, TailDrop


DUMMY_TASK = "whatever"


class NoThrottlingTests(TestCase):

    def test_never_rejects(self):
        throttling = NoThrottling(MagicMock(TaskPool));
        self.assertTrue(throttling._accepts(DUMMY_TASK))


class TailDropTests(TestCase):

    def setUp(self):
        self.capacity = 50
        self.queue = MagicMock(TaskPool)
        self.pool_size(50)
        self.throttling = TailDrop(self.queue, self.capacity)

    def pool_size(self, length):
        type(self.queue).size = PropertyMock(return_value=length)

    def test_rejects_non_integer_capacity(self):
        try:
            capacity = "not an integer"
            TailDrop(self.queue, capacity)
            self.fail("AssertionError expected!")

        except AssertionError as error:
            self.assertEqual(error.args[0], TailDrop.INVALID_CAPACITY.format(object=capacity))

    def test_rejects_negative_capacity(self):
        try:
            capacity = -5
            TailDrop(self.queue, capacity)
            self.fail("AssertionError expected!")

        except AssertionError as error:
            self.assertEqual(error.args[0], TailDrop.NEGATIVE_CAPACITY.format(capacity=capacity))

    def test_reject_at_capacity(self):
        self.pool_size(self.capacity)
        self.assertFalse(self.throttling._accepts(DUMMY_TASK))

    def test_reject_beyond_capacity(self):
        self.pool_size(self.capacity + 1)
        self.assertFalse(self.throttling._accepts(DUMMY_TASK))

    def test_accept_before_capacity(self):
        self.pool_size(self.capacity - 1)
        self.assertTrue(self.throttling._accepts(DUMMY_TASK))



if __name__ == "__main__":
    from unittest import main
    main()