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
        self.tasks = []
        self.interrupted = []

    def put(self, request):
        self.tasks.append(request)

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

    @property
    def are_pending(self):
        return not self.is_empty

    @property
    def size(self):
        return len(self.tasks) + len(self.interrupted)

    def activate(self, task):
        self.interrupted.append(task)


class FIFOTaskPool(TaskPool):

    def __init__(self):
        super().__init__()

    def _next(self, candidates):
        selected = candidates[0]
        self._remove(selected)
        return selected


class LIFOTaskPool(TaskPool):

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

    @property
    def priority(self):
        return self.request.priority

    def mark_as_started(self):
        self.is_started = True
