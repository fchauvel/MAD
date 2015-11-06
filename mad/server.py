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
from collections import namedtuple

from mad.engine import Agent, CompositeAgent, Action
from mad.throttling import StaticThrottling
from mad.scalability import Controller, UtilisationController
from mad.backoff import ExponentialBackOff
from mad.client import Request, Send, Meter


Service = namedtuple("Service", ["endpoint", "back_off"])

class Server(CompositeAgent):
    """
    The server receives request and returns a response
    """

    def __init__(self, identifier, service_rate=0.2, throttling=StaticThrottling(0), scalability=Controller(0.4), back_off=ExponentialBackOff.factory):
        super().__init__(identifier)
        self._service_rate = service_rate
        self._queue = Queue()
        self._meter = Meter()
        self._cluster = Cluster(self)
        self._throttling = throttling
        self._throttling.queue = self._queue
        self._scalability = scalability
        self._scalability.cluster = self._cluster
        self._back_off_factory = back_off
        self._back_ends = []

    @CompositeAgent.agents.getter
    def agents(self):
        return [self._queue, self._cluster, self._scalability]

    def record_composite_state(self):
        self.record([("queue length", "%d", self._queue.length),
                     ("rejection count", "%d", self._meter.rejection_count),
                     ("utilisation", "%f", self._cluster.utilisation),
                     ("unit count", "%d", self._cluster.active_unit_count),
                     ("response time", "%d", self.response_time),
                     ("request count", "%d", self._meter.request_count)
                     ])
        self._meter.reset()

    def composite_setup(self):
        self.initialize_recorder()

    @property
    def back_ends(self):
        return self._back_ends

    @back_ends.setter
    def back_ends(self, new_back_end_list):
        self.back_ends.clear()
        for each_back_end in new_back_end_list:
            back_off = self._back_off_factory()
            self._back_ends.append(Service(each_back_end, back_off))

    @property
    def queue(self):
        return self._queue

    @property
    def meter(self):
        return self._meter

    @property
    def service_rate(self):
        return self._service_rate

    def process(self, request):
        self._meter.new_request()
        if self._throttling.accepts(request):
            self._queue.put(request)
            self._cluster.new_request()
        else:
            self._meter.new_rejection()
            request.reject()

    @property
    def utilisation(self):
        return self._cluster.utilisation

    @property
    def queue_length(self):
        return self._queue.length

    @property
    def response_time(self):
        return self._meter.average_response_time

    def create_unit(self):
        new_unit = ProcessingUnit(self)
        new_unit.clock = self.clock
        new_unit.setup()
        return new_unit

    def destroy_unit(self, unit):
        self._cluster.discard(unit)


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

    def put(self, request):
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

    def __init__(self, server):
        super().__init__(Cluster.KEY)
        self._server = server
        self._units = [self._server.create_unit()]

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
        self._units.append(self._server.create_unit())

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


class StartProcessing(Action):

    def __init__(self, subject):
        self._subject = subject

    def fire(self):
        self._subject.start_processing()


class Retry(Action):

    def __init__(self, request, destination):
        self._request = request
        self._destination = destination

    def fire(self):
        self._request.send_to(self._destination)


class ProcessingUnit(Agent):
    """
    Represent a single processing unit, i.e., a "server" in queueing systems parlance
    """

    COUNTER = 0

    def __init__(self, server):
        ProcessingUnit.COUNTER += 1
        super().__init__("Unit#%d" % ProcessingUnit.COUNTER)
        self._server = server
        self._destination = {}
        self._request = None
        self._stopped = False

    def process(self):
        if not self._server.queue.is_empty:
            self._request = self._server.queue.take()
            if len(self._server.back_ends) > 0:
                self.schedule_in(StartProcessing(self), self.service_time)
            else:
                self.schedule_in(Completion(self), self.service_time)

    def start_processing(self):
        for each_back_end in self._server.back_ends:
            request = Request(self)
            self._destination[request] = each_back_end
            request.send_to(each_back_end.endpoint)

    def on_completion_of(self, request):
        self._destination[request].back_off.new_success()
        if self.all_back_ends_have_replied():
            self.complete()

    def all_back_ends_have_replied(self):
        return all([each_request.is_replied for each_request in self._destination.keys()])

    def complete(self):
        assert self.is_busy, "An idle unit cannot complete the processing of a request"
        self._request.reply()
        self._server.meter.new_success(self._request)
        self._request = None
        if self._stopped:
            self._server.destroy_unit(self)
        else:
            self.process()

    def stop(self):
        self._stopped = True
        if self.is_idle:
            self._server.destroy_unit(self)

    def on_rejection_of(self, request):
        self._destination[request].back_off.new_rejection()
        retry = Retry(request, self._destination[request].endpoint)
        self.schedule_in(retry, self._destination[request].back_off.delay)

    @property
    def service_time(self):
        return int(1 / self._server.service_rate)

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




