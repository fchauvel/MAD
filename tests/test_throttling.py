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

from mad.server import Queue
from mad.throttling import StaticThrottling, RandomEarlyDetection


class REDThrottlingPolicy(TestCase):

    def test_RED_do_not_throttle_when_queue_is_empty(self):
        queue = MagicMock(Queue)
        type(queue).length = PropertyMock(return_value=0)
        throttling = RandomEarlyDetection(queue, 25)
        self.assertTrue(throttling.accepts(None))

    def test_RED_throttle_when_queue_is_full(self):
        queue = MagicMock(Queue)
        type(queue).length = PropertyMock(return_value=25)
        throttling = RandomEarlyDetection(queue, 25)
        self.assertTrue(throttling.rejects(None))


class StaticRejectionPolicy(TestCase):

    def test_never_throttle_anything(self):
        server = MagicMock(Queue)
        throttling = StaticThrottling(server, 0)
        self.assertTrue(throttling.accepts(None))

    def test_never_throttle_anything(self):
        server = MagicMock(Queue)
        throttling = StaticThrottling(server, 1)
        self.assertTrue(throttling.rejects(None))


if __name__ == "__main__":
    main()