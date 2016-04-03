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


class WorkerPool:
    """
    Represent a pool of workers that can take over a simple task
    """

    def __init__(self, workers):
        assert len(workers) > 0, "Cannot build a worker pool without any worker!"
        self.capacity = len(workers)
        self.idle_workers = workers

    def add_workers(self, new_workers):
        assert len(new_workers) > 0, "Cannot add empty list of workers!"
        self.idle_workers.extend(new_workers)
        self.capacity += len(new_workers)

    def shutdown(self, count):
        assert count < self.capacity, "Invalid shutdown %d (capacity %d)" % (count, self.capacity)
        self.capacity -= count
        for index in range(min(len(self.idle_workers), count)):
            self.idle_workers.pop(0)


    @property
    def utilisation(self):
        return 100 * (1 - (len(self.idle_workers) / self.capacity))

    @property
    def idle_worker_count(self):
        return len(self.idle_workers)

    @property
    def are_available(self):
        return len(self.idle_workers) > 0

    def acquire_one(self):
        if not self.are_available:
            raise ValueError("Cannot acquire from an empty worker pool!")
        return self.idle_workers.pop(0)

    def release(self, worker):
        if len(self.idle_workers) < self.capacity:
            self.idle_workers.append(worker)
        # Discard otherwise (it has been shutdown)


class Worker(SimulatedEntity):
    """
    Represent a worker (i.e., a thread, or a service replica) that handles requests
    """

    def __init__(self, identifier, environment):
        super().__init__("Worker %d" % identifier, environment)
        self.environment.define(Symbols.WORKER, self)
        self.identifier = identifier

    def assign(self, task):
        def release_worker(result):
            service = self.look_up(Symbols.SERVICE)
            service.release(self)

        if task.is_started:
            task.resume(self)
        else:
            task.mark_as_started()
            operation = self.look_up(task.request.operation)
            operation.invoke(task, [], release_worker, self)
