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

from enum import Enum

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

    def take(self):
        task = super().take()
        return task

    def activate(self, task):
        super().activate(task)


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
        task.accept()
        task.activate()
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


class TaskStatus(Enum):
    CREATED, RUNNING, BLOCKED, READY, REJECTED, FAILED, SUCCESSFUL = range(7)


class Task:

    def __init__(self, service, request=None):
        self.service = service
        self.worker = None
        self.request = request
        self.status = TaskStatus.CREATED

    @property
    def priority(self):
        return self.request.priority

    @property
    def identifier(self):
        return self.request.identifier

    @property
    def is_cancelled(self):
        return not self.request.is_pending

    @property
    def operation(self):
        return self.request.operation

    def accept(self):
        self._assert_status_is(TaskStatus.CREATED)
        self.service.listener.task_accepted(self)
        self.request.accept()

    def reject(self):
        self._assert_status_is(TaskStatus.CREATED)
        self.service.listener.task_rejected(self)
        self.status == TaskStatus.REJECTED
        self.request.reject()

    def activate(self):
        self._assert_status_is(TaskStatus.CREATED, TaskStatus.BLOCKED)
        self.service.listener.task_activated(self)
        self.status = TaskStatus.READY

    def assign_to(self, worker):
        assert worker, "task assigned to None!"
        self._assert_status_is(TaskStatus.CREATED, TaskStatus.READY)

        self.worker = worker
        if self.is_cancelled:
            self.discard()
        else:
            self.service.listener.task_assigned_to(self, worker)
            self.status = TaskStatus.RUNNING
            self._execute(worker)

    def _execute(self, worker):
        """
        This method is ASSIGNED during the evaluation to control how to resume it once it has been paused
        """
        self._assert_status_is(TaskStatus.RUNNING)
        operation = worker.look_up(self.operation)
        operation.invoke(self, [], worker=worker)

    def pause(self):
        self._assert_status_is(TaskStatus.RUNNING)
        self.service.listener.task_paused(self)
        self.status = TaskStatus.BLOCKED
        self.service.pause(self)
        self.service.release(self.worker)

    def resume_with(self, on_resume):
        self._assert_status_is(TaskStatus.BLOCKED)
        self._execute = on_resume
        self.service.activate(self)

    def compute(self, duration, continuation):
        assert self.worker is not None, "Cannot compute, no worker attached!"
        self.worker.compute(duration, continuation)

    def finalise(self, status):
        self.request.finalise(self, status)

    def succeed(self):
        self._assert_status_is(TaskStatus.RUNNING)
        self.service.listener.task_successful(self)
        self.status = TaskStatus.SUCCESSFUL
        self.service.release(self.worker)

    def discard(self):
        self._assert_status_is(TaskStatus.CREATED, TaskStatus.RUNNING, TaskStatus.READY)
        self.worker.listener.task_cancelled(self)
        self.status = TaskStatus.FAILED
        self.worker.release()

    def fail(self):
        self._assert_status_is(TaskStatus.RUNNING)
        self.service.listener.task_failed(self)
        self.status == TaskStatus.FAILED
        self.service.release(self.worker)

    def _assert_status_is(self, *legal_states):
        assert self.status in legal_states, \
            "Found status == {0.name} (expecting {1!s})".format(self.status, [ s.name for s in legal_states ])
