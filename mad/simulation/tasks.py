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


class TaskPool:

    def __init__(self):
        self.requests = []

    def put(self, request):
        self.requests.append(request)

    def take(self):
        raise NotImplementedError("TaskPool::take is abstract!")

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def are_pending(self):
        return not self.is_empty

    @property
    def size(self):
        return len(self.requests)

    def activate(self, request):
        raise NotImplementedError("TaskPool::activate is abstract!")


class FIFOTaskPool(TaskPool):

    def __init__(self):
        super().__init__()

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take a request from an empty pool!")
        return self.requests.pop(0)

    def activate(self, request):
        self.requests.insert(0, request)


class LIFOTaskPool(TaskPool):

    def __init__(self):
        super().__init__()

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take a request from an empty pool!")
        return self.requests.pop(-1)

    def activate(self, request):
        self.requests.append(request)


class Task:

    def __init__(self, request=None):
        self.request = request
        self.is_started = False
        self.resume = lambda: None

    def mark_as_started(self):
        self.is_started = True
