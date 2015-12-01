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
from mock import MagicMock, PropertyMock

from mad.client import Request
from mad.queueing import Queue
from mad.throttling import StaticThrottling, TailDrop, RED


class TestRED(TestCase):

    def _fake_queue(self, sizes):
        queue = MagicMock(Queue)
        type(queue).length = PropertyMock(side_effect=sizes)
        return queue

    def test_average_queue_length(self):
        throttling = RED(10, 15, 1.0, 0.25)
        throttling.queue = self._fake_queue(sizes=[5,6,7,8])

        self.assertTrue(throttling.accepts(MagicMock(Request)))

    def test_average_queue_length(self):
        throttling = RED(10, 15, 1.0, 0.25)
        throttling._avg = 20
        throttling.queue = self._fake_queue(sizes=[25,26,27,28])

        self.assertTrue(throttling.rejects(MagicMock(Request)))


class StaticRejectionPolicy(TestCase):

    def test_never_throttle_anything(self):
        throttling = StaticThrottling(0)
        throttling.queue = MagicMock(Queue)

        self.assertTrue(throttling.accepts(None))

    def test_never_throttle_anything(self):
        throttling = StaticThrottling(1)
        throttling.queue =  MagicMock(Queue)

        self.assertTrue(throttling.rejects(None))


class TestTailDrop(TestCase):

    def test_reject_when_queue_is_full(self):
        throttling = TailDrop(capacity=5)
        throttling.queue = MagicMock(Queue)
        type(throttling.queue).length = PropertyMock(side_effect=[5])

        self.assertTrue(throttling.rejects(None))

    def test_accepts_when_queue_is_not_full(self):
        throttling = TailDrop(capacity=5)
        throttling.queue = MagicMock(Queue)
        type(throttling.queue).length = PropertyMock(side_effect=[2])

        self.assertTrue(throttling.accepts(MagicMock(Request)))


if __name__ == "__main__":
    main()