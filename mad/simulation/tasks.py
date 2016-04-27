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


class TaskPool:

    def put(self, task):
        raise NotImplementedError("TaskPool::put is abstract")

    def take(self):
        raise NotImplementedError("TaskPool::take is abstract")

    @property
    def size(self):
        raise NotImplementedError("TaskPool::size is abstract")

    @property
    def blocked_count(self):
        raise NotImplementedError("TaskPool::size is abstract")

    @property
    def are_pending(self):
        raise NotImplementedError("TaskPool::are_pending is abstract")

    def activate(self, task):
        raise NotImplementedError("TaskPool::activate is abstract")

    def pause(self, task):
        raise NotImplementedError("TaskPool::pause is abstract")

    def intercept(self, task):
        raise NotImplementedError("TaskPool::intercept is abstract")


class TaskPoolDecorator(TaskPool):

    def __init__(self, delegate):
        assert isinstance(delegate, TaskPool), "Delegate should be a TaskPool (found '{!s}')".format(type(delegate))
        self.delegate = delegate

    def put(self, task):
        self.delegate.put(task)

    def take(self):
        return self.delegate.take()

    @TaskPool.size.getter
    def size(self):
        return self.delegate.size

    @TaskPool.blocked_count.getter
    def blocked_count(self):
        return self.delegate.blocked_count

    @TaskPool.are_pending.getter
    def are_pending(self):
        return self.delegate.are_pending

    def activate(self, task):
        self.delegate.activate(task)

    def pause(self, task):
        self.delegate.pause(task)

    def intercept(self, task):
        self.delegate.intercept(task)


class TaskPoolWrapper(TaskPoolDecorator, SimulatedEntity):
    """
    Wrap a task pool into a simulation entity that that properly log events
    """

    def __init__(self, environment, delegate):
        SimulatedEntity.__init__(self, Symbols.QUEUE, environment)
        TaskPoolDecorator.__init__(self, delegate)

    def put(self, task):
        super().put(task)
        self.listener.storage_of(task.request)

    def take(self):
        task = super().take()
        self.listener.selection_of(task.request)
        return task

    def activate(self, task):
        super().activate(task)
        self.listener.resuming(task.request)


class AbstractTaskPool(TaskPool):

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.interrupted = []
        self.paused = []

    def pause(self, task):
        self.paused.append(task)

    def intercept(self, task):
        self.paused.remove(task)

    def put(self, task):
        task.request.accept()
        self.tasks.append(task)

    def take(self):
        if len(self.interrupted) > 0:
            return self._pick_from(self.interrupted)
        else:
            if len(self.tasks) > 0:
                return self._pick_from(self.tasks)
            raise ValueError("Unable to take from an empty task pool!")

    def _pick_from(self, candidates):
        high_priority = self._highest_priority(candidates)
        return self._next( high_priority)

    @staticmethod
    def _highest_priority(candidates):
        highest = max(candidates, key=lambda task: task.priority)
        return [any_task for any_task in candidates if any_task.priority == highest.priority]

    def _next(self, candidates):
        raise NotImplementedError("TaskPool::_next is abstract!")

    def _remove(self, task):
        if task in self.tasks: self.tasks.remove(task)
        if task in self.interrupted: self.interrupted.remove(task)

    @property
    def is_empty(self):
        return self.size == 0

    @TaskPool.are_pending.getter
    def are_pending(self):
        return not self.is_empty

    @TaskPool.size.getter
    def size(self):
        return len(self.tasks) + len(self.interrupted)

    @TaskPool.blocked_count.getter
    def blocked_count(self):
        return len(self.paused)

    def activate(self, task):
        assert task in self.paused, "Error: Req. {:d} should have been paused!".format(task.request.identifier)
        self.paused.remove(task)
        self.interrupted.append(task)


class FIFOTaskPool(AbstractTaskPool):

    def __init__(self):
        super().__init__()

    def _next(self, candidates):
        selected = candidates[0]
        self._remove(selected)
        return selected


class LIFOTaskPool(AbstractTaskPool):

    def __init__(self):
        super().__init__()

    def _next(self, candidates):
        selected = candidates[-1]
        self._remove(selected)
        return selected


class Task:

    def __init__(self, request=None):
        self.request = request
        self.is_started = False
        self.resume = lambda: None

    def reject(self):
        self.request.reply_error()

    @property
    def priority(self):
        return self.request.priority

    def mark_as_started(self):
        self.is_started = True
