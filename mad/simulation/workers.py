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
        self.idle_workers = workers
        self.busy_workers = []
        self.stopped_workers = []

    @property
    def capacity(self):
        return len(self.idle_workers) + len(self.busy_workers)

    def add_workers(self, new_workers):
        assert len(new_workers) > 0, "Cannot add empty list of workers!"
        self.idle_workers.extend(new_workers)

    def shutdown(self, count):
        assert count < self.capacity, "Invalid shutdown %d (capacity %d)" % (count, self.capacity)
        for index in range(count):
            if len(self.idle_workers) > 0:
                self.idle_workers.pop(0)
            else:
                assert len(self.busy_workers) > 0
                stopped_worker = self.busy_workers.pop(0)
                self.stopped_workers.append(stopped_worker)

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
        busy_worker = self.idle_workers.pop(0)
        self.busy_workers.append(busy_worker)
        return busy_worker

    def release(self, worker):
        assert worker not in self.idle_workers, "Error: Cannot release an idle worker!"
        if worker in self.busy_workers:
            self.idle_workers.append(worker)
            self.busy_workers.remove(worker)
        else:
            assert worker in self.stopped_workers, "Error: Unknown worker (not idle, not busy, not stopped)!"
            self.stopped_workers.remove(worker)


class Worker(SimulatedEntity):
    """
    Represent a worker (i.e., a thread, or a service replica) that handles requests
    """

    def __init__(self, identifier, environment):
        super().__init__("Worker %d" % identifier, environment)
        self.environment.define(Symbols.WORKER, self)
        self.identifier = identifier

    def assign(self, task):
        if task.request.is_pending:
            if task.is_started:
                task.resume(self)
            else:
                task.mark_as_started()
                operation = self.look_up(task.request.operation)
                operation.invoke(task, [], worker=self)
                # the worker will be released from the evaluation of the operation
        else:
            self.listener.error_replied_to(task.request) # log the timeout as an error
