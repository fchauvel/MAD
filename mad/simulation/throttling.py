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

from mad.simulation.tasks import TaskPool

NEGATIVE_CAPACITY = "Capacity must be strictly positive, but found {capacity:d}"
INVALID_CAPACITY = "Capacity must be an integer, but found '{object.__class__.__name__:s}'"
INVALID_TASK_POOL = "TaskPool object required, but found '{object.__class__.__name__:s}'"


class ThrottlingPolicy(TaskPool):
    """
    Common interface of all throttling policies
    """

    def __init__(self, tasks):
        self.tasks = tasks

    def take(self):
        return self.tasks.take()

    def put(self, task):
        if self._accepts(task):
            self.tasks.put(task)
        else:
            task.reject()

    def _accepts(self, task):
        raise NotImplementedError("Throttling:_do_accept is abstract!")

    @TaskPool.are_pending.getter
    def are_pending(self):
        return self.tasks.are_pending

    @TaskPool.size.getter
    def size(self):
        return self.tasks.size

    def activate(self, task):
        self.tasks.activate(task)


class NoThrottling(ThrottlingPolicy):
    """
    Default policy: Always accept requests.
    """
    def __init__(self, tasks):
        super().__init__(tasks)

    def _accepts(self, task):
        return True;


class TailDrop(ThrottlingPolicy):
    """
    Reject requests once the given task pool size reaches the
    specified capacity
    """

    def __init__(self, task_pool, capacity):
        super().__init__(task_pool)
        assert isinstance(capacity, int), INVALID_CAPACITY.format(object=capacity)
        assert capacity > 0, NEGATIVE_CAPACITY.format(capacity=capacity)
        self.capacity = capacity

    def _accepts(self, task):
        return self.tasks.size < self.capacity
