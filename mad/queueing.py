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


from mad.des import Agent


class Queue:
    """
    Queue class, by default a FIFO queue
    """

    @classmethod
    def fifo(cls, content):
        return Queue(content, next=0)

    @classmethod
    def lifo(cls, content):
        return Queue(content, next=-1)

    def __init__(self, content=[], next=0):
        self._queue = content
        self._next = next

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take from an empty queue!")
        return self._queue.pop(self._next)

    def put(self, request):
        self._queue.append(request)

    @property
    def is_empty(self):
        return len(self._queue) == 0

    @property
    def length(self):
        return len(self._queue)
