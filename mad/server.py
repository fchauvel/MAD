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

from random import choice

from mad.engine import Agent, CompositeAgent, Action
from mad.throttling import StaticThrottling
from mad.scalability import Controller, UtilisationController


class Server(CompositeAgent):
    """
    The server receives request and returns a response
    """

    def __init__(self, identifier, service_rate=0.2, throttling=StaticThrottling(0), scalability=Controller(0.4)):
        super().__init__(identifier)
        self._service_rate = service_rate
        self._queue = Queue()
        self._cluster = Cluster(self._queue, service_rate)
        self._throttling = throttling
        self._scalability = scalability
        self._scalability.cluster = self._cluster

    @CompositeAgent.agents.getter
    def agents(self):
        return [self._queue, self._cluster, self._scalability]

    def composite_setup(self):
        self.initialize_recorder()

    def process(self, request):
        if self._throttling.accepts(request):
            self._queue.append(request)
            self._cluster.new_request()
        else:
            request.reject()

    @property
    def utilisation(self):
        return self._cluster.utilisation

    @property
    def queue_length(self):
        return self._queue.length

    def record_composite_state(self):
        self.record([("queue length", "%d", self._queue.length),
                     ("rejection rate", "%f", self._throttling.rejection_rate),
                     ("utilisation", "%f", self._cluster.utilisation),
                     ("unit count", "%d", self._cluster.active_unit_count)])


class Queue(Agent):
    """
    Represent a queue of requests to be processed
    """

    IDENTIFIER = "queue"

    def __init__(self):
        super().__init__(Queue.IDENTIFIER)
        self._queue = []

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take from an empty queue!")
        return self._queue.pop(0)

    def append(self, request):
        self._queue.append(request)

    @property
    def is_empty(self):
        return len(self._queue) == 0

    @property
    def length(self):
        return len(self._queue)


class Cluster(CompositeAgent):
    """
    A cluster of processing units
    """

    KEY = "cluster"

    def __init__(self, queue, service_rate):
        super().__init__(Cluster.KEY)
        self._service_rate = service_rate
        self._queue = queue
        self._units = [ProcessingUnit(self, queue, service_rate)]

    @CompositeAgent.agents.getter
    def agents(self):
        return self._units

    def new_request(self):
        for any_unit in self._units:
            if any_unit.is_idle:
                any_unit.process()
                break

    @property
    def utilisation(self):
        if len(self._units) > 0:
            return len(self.busy_units) / len(self._units) * 100
        else:
            return 100

    @property
    def busy_units(self):
        return [ any_unit for any_unit in self._units if any_unit.is_busy ]

    @property
    def idle_units(self):
        return [ any_unit for any_unit in self._units if any_unit.is_idle ]

    @property
    def active_units(self):
        return [ any_unit for any_unit in self._units if any_unit.is_active ]

    @property
    def active_unit_count(self):
        return len(self.active_units)

    @active_unit_count.setter
    def active_unit_count(self, new_count):
        count = self.active_unit_count
        missing_units = new_count - count
        if missing_units > 0:
            for i in range(missing_units):
                self._grow()
        elif missing_units < 0:
            for i in range(max(0, new_count), count):
                self._shrink()

    def _grow(self):
        self._units.append(ProcessingUnit(self, self._queue, self._service_rate))

    def _shrink(self):
        assert self.active_unit_count > 0, "Cannot shrink, no more unit!"
        choice(self.active_units).stop()

    def discard(self, unit):
        assert unit.is_stopped, "Cannot discard unit '%s', it is not stopped" % unit.identifier
        self._units.remove(unit)


class Completion(Action):
    """
    Completion of the processing a single request
    """

    def __init__(self, subject):
        self._subject = subject

    def fire(self):
        self._subject.complete()


class ProcessingUnit(Agent):

    COUNTER = 0

    def __init__(self, cluster, queue, service_rate):
        ProcessingUnit.COUNTER += 1
        super().__init__("Unit#%d" % ProcessingUnit.COUNTER)
        self._cluster = cluster
        self._service_rate = service_rate
        self._queue = queue
        self._request = None
        self._stopped = False

    def process(self):
        if not self._queue.is_empty:
            self._request = self._queue.take()
            self.schedule_in(Completion(self), self.service_time)

    @property
    def service_time(self):
        return int(1 / self._service_rate)

    @property
    def is_idle(self):
        return self._request is None

    @property
    def is_busy(self):
        return not self.is_idle

    @property
    def is_active(self):
        return not self.is_stopped

    @property
    def is_stopped(self):
        return self._stopped

    def complete(self):
        assert self.is_busy, "An idle unit cannot complete the processing of a request"
        self._request.reply()
        self._request = None
        if self._stopped:
            self._cluster.discard(self)
        else:
            self.process()

    def stop(self):
        self._stopped = True
        if self.is_idle:
            self._cluster.discard(self)


