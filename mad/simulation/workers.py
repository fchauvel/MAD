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


class WorkerPoolDecorator(WorkerPool):

    def __init__(self, delegate):
        self.delegate = delegate

    def __getattr__(self, name):
        return getattr(self.delegate, name)


class WorkerPoolWrapper(SimulatedEntity, WorkerPoolDecorator):

    def __init__(self, environment, delegate):
        SimulatedEntity.__init__(self, Symbols.WORKER_POOL, environment)
        WorkerPoolDecorator.__init__(self, delegate)

    def _new_worker(self, identifier):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.SERVICE, self)
        return self.factory.create_worker(identifier, environment)

    def set_capacity(self, capacity):
        error = self.capacity - capacity
        if error < 0:
            new_workers = [self._new_worker(id) for id in range(-error)] # FIXME: worker ID seems wrong
            self.add_workers(new_workers)
        elif error > 0:
            self.shutdown(error)


class WorkerStatus(Enum):
    STARTING, IDLE, BUSY = range(3)


class Worker(SimulatedEntity):
    """
    Represent a worker (i.e., a thread, or a service replica) that handles requests
    """

    def __init__(self, identifier, environment):
        super().__init__("Worker %d" % identifier, environment)
        self.environment.define(Symbols.WORKER, self)
        self.identifier = identifier

    def boot_up(self):
        # TODO: block the thread for some time, by calling compute
        pass

    def perform(self):
        # TODO: notify the listener that the thread is active
        pass

    def compute(self, duration, continuation):
        self.simulation.schedule.after(duration, continuation)

    def release(self):
        # TODO change the meaning of this operation (it should be called by the service/scheduler)
        # TODO notify the listener that the thread is idle
        service = self.look_up(Symbols.SERVICE)
        service.release(self)

    def shutdown(self):
        # TODO: notify that the thread is shutting down
        pass