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


from random import random


class ThrottlingPolicy:
    """
    Interface of the throttling policies
    """

    def __init__(self):
        self._queue = None

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, new_queue):
        self._queue = new_queue

    def rejects(self, request):
        pass

    def accepts(self, request):
        return not self.rejects(request)


class StaticThrottling(ThrottlingPolicy):
    """
    Reject request based on a redefined rejection rate.
    """

    def __init__(self, rejection_rate=0.):
        super().__init__()
        self._rejection_rate = rejection_rate

    @property
    def rejection_rate(self):
        return self._rejection_rate

    @rejection_rate.setter
    def rejection_rate(self, new_rate):
        self._rejection_rate = new_rate

    def rejects(self, request):
        return random() < self.rejection_rate


class TailDrop(ThrottlingPolicy):
    """
    Tail drop: reject all the request once the queue is filled up to capacity
    """

    def __init__(self, capacity):
        super().__init__()
        self._capacity = capacity

    def rejects(self, request):
        return self._queue_is_full()

    def _queue_is_full(self):
        return self._queue.length >= self._capacity


class RED(ThrottlingPolicy):

    def __init__(self, min, max, maxp=1., w=0.25):
        assert min >= 0, "Minimum queue length must be positive"
        assert max >= 0, "Maximum queue length must be positive"
        assert max > min, "min must be greater than max"
        assert 0 <= maxp <= 1, "maxp must be within [0, 1]"
        self._min = min
        self._max = max
        self._maxp = maxp
        self._w = w
        self._avg = 0
        self._count = -1

    def rejects(self, request):
        self._adjust_average_queue_length()
        print("QL: %d ; AVG-QL: %.2f" % (self.queue.length, self._avg), end="\n")
        if self._min <= self._avg < self._max:
            self._count += 1
            if random() < self._threshold:
                self._count = 0
                return True
        elif self._avg >= self._max:
            self._count = 0
            return True
        else:
            self._count = -1
            return False

    def _adjust_average_queue_length(self):
        self._avg = self._avg * (1 - self._w) + self._w * self.queue.length

    @property
    def _threshold(self):
        pb = self._maxp * self._queue_level
        return pb / (1 - self._count * pb)

    @property
    def _queue_level(self):
        return (self._avg - self._min) / (self._max - self._min)
