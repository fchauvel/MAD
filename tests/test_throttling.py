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
from mad.server import Queue
from mad.throttling import StaticThrottling, RandomEarlyDetection, TailDrop


class REDThrottlingPolicy(TestCase):

    def test_RED_do_not_throttle_when_queue_is_empty(self):
        queue = MagicMock(Queue)
        type(queue).length = PropertyMock(return_value=0)

        throttling = RandomEarlyDetection(25)
        throttling.queue = queue

        self.assertTrue(throttling.accepts(None))

    def test_RED_throttle_when_queue_is_full(self):
        queue = MagicMock(Queue)
        type(queue).length = PropertyMock(return_value=25)

        throttling = RandomEarlyDetection(25)
        throttling.queue = queue

        self.assertTrue(throttling.rejects(None))


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