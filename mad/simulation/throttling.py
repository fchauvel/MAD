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

from mad.evaluation import Symbols
from mad.simulation.commons import SimulatedEntity
from mad.simulation.tasks import TaskPoolDecorator


class ThrottlingPolicy(TaskPoolDecorator):
    """
    Common interface of all throttling policies
    """

    def __init__(self, task_pool):
        super().__init__(task_pool)

    def put(self, task):
        if self._accepts(task):
            self.delegate.put(task)
        else:
            task.reject()
            self._reject(task)

    def _accepts(self, task):
        raise NotImplementedError("Throttling:_accepts is abstract!")

    def _reject(self, task):
        task.reject()


class ThrottlingPolicyDecorator(ThrottlingPolicy):

    def __init__(self, delegate):
        super().__init__(delegate)
        self.delegate = delegate

    def _accepts(self, task):
        return self.delegate._accepts(task)

    def _reject(self, task):
        self.delegate._reject(task)


class NoThrottling(ThrottlingPolicy):
    """
    Default policy: Always accept requests.
    """
    def __init__(self, task_pool):
        super().__init__(task_pool)

    def _accepts(self, task):
        return True;


class TailDrop(ThrottlingPolicy):
    """
    Reject requests once the given task pool size reaches the
    specified capacity
    """
    NEGATIVE_CAPACITY = "Capacity must be strictly positive, but found {capacity:d}"
    INVALID_CAPACITY = "Capacity must be an integer, but found '{object.__class__.__name__:s}'"

    def __init__(self, task_pool, capacity):
        super().__init__(task_pool)
        assert isinstance(capacity, int), self.INVALID_CAPACITY.format(object=capacity)
        assert capacity > 0, self.NEGATIVE_CAPACITY.format(capacity=capacity)
        self.capacity = capacity

    def _accepts(self, task):
        return self.delegate.size < self.capacity


class ThrottlingWrapper(SimulatedEntity, ThrottlingPolicyDecorator):

    def __init__(self, environment, task_pool):
        SimulatedEntity.__init__(self, Symbols.QUEUE, environment)
        ThrottlingPolicyDecorator.__init__(self, task_pool)

    def _reject(self, task):
        super()._reject(task)
        self.listener.rejection_of(task.request)
