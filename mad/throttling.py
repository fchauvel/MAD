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


class RandomEarlyDetection(StaticThrottling):
    """
    Random Early Detection algorithm, which increases the rejection rate as the queue filled in
    """

    def __init__(self, capacity):
        super().__init__()
        self._capacity = capacity

    def rejects(self, request):
        self.rejection_rate = (self.queue.length / self._capacity)
        return super().rejects(request)
