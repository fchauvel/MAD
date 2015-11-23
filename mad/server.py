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

from mad.math import Constant
from mad.des import Agent, CompositeAgent, Action
from mad.throttling import StaticThrottling
from mad.autoscaling import Controller, UtilisationThreshold
from mad.backoff import ExponentialBackOff
from mad.client import Request, Send, Meter


Service = namedtuple("Service", ["endpoint", "back_off", "meter"])


class ServiceStub(Agent):
    """
    A service stub, on which one can adjust the response time and the rejection rate
    """

    def __init__(self, name="Service Stub", response_time=10, rejection_rate=0.1):
        super().__init__(name)
        self._response_time = response_time
        self._throttling = StaticThrottling(rejection_rate)

    @property
    def response_time(self):
        return self._response_time

    @response_time.setter
    def response_time(self, new_response_time):
        self._response_time = new_response_time

    @property
    def rejection_rate(self):
        return self.rejection_rate

    @rejection_rate.setter
    def rejection_rate(self, new_rejection_rate):
        self._throttling = StaticThrottling(new_rejection_rate)

    def process(self, request):
        if self._throttling.accepts(request):
            self.schedule_in(Reply(self, request), self._response_time)
        else:
            request.reject()


class Reply(Action):
    """
    Reply to the given request
    """

    def __init__(self, subject, request):
        self._subject = subject
        self._request = request

    def fire(self):
        self._request.reply()

    def __str__(self):
        return "replying to request"


class Server(CompositeAgent):
    """
    The server receives request and returns a response
    """

    def __init__(self, identifier, service_time=Constant(5), throttling=StaticThrottling(0), scalability=Controller(10), back_off=ExponentialBackOff.factory):
        super().__init__(identifier)
        self._service_time = service_time
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

    def state_entries(self):
        entries = [("queue length", "%d", self._queue.length),
                     ("rejection count", "%d", self._meter.rejection_count),
                     ("utilisation", "%f", self._cluster.utilisation),
                     ("unit count", "%d", self._cluster.active_unit_count),
                     ("response time", "%d", self.response_time),
                     ("request count", "%d", self._meter.request_count),
                     ("throughput", "%d", self._meter.throughput)]

        for each_back_end in enumerate(self._back_ends):
            emission_rate = ("emission count %d" % each_back_end[0], "%d", each_back_end[1].meter.request_count)
            entries.append(emission_rate)

        self._meter.reset()
        for each_back_end in self._back_ends:
            each_back_end.meter.reset()

        return entries

    @property
    def back_ends(self):
        return self._back_ends

    @back_ends.setter
    def back_ends(self, new_back_end_list):
        self.back_ends.clear()
        for each_back_end in new_back_end_list:
            back_off = self._back_off_factory()
            self._back_ends.append(Service(each_back_end, back_off, Meter()))

    @property
    def queue(self):
        return self._queue

    @property
    def meter(self):
        return self._meter

    @property
    def service_time(self):
        return self._service_time.value_at(self.current_time)

    def process(self, request):
        self._meter.new_request()
        if self._throttling.accepts(request):
            self._queue.put(request)
            self._cluster.check_out_for_requests()
        else:
            self.log("request rejected")
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
        new_unit.trace = self.trace
        new_unit.on_start()
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
        self.log("request enqueued (length = %d)" % self.length)
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

    def check_out_for_requests(self):
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
        new_unit = self._server.create_unit()
        new_unit.container = self
        self._units.append(new_unit)
        new_unit.process()

    def _shrink(self):
        assert self.active_unit_count > 0, "Cannot shrink, no more unit!"
        choice(self.active_units).stop()

    def discard(self, unit):
        assert unit.is_stopped, "Cannot discard unit '%s', it is not stopped" % unit.identifier
        self.log("Terminating %s" % unit.identifier)
        self._units.remove(unit)


class Completion(Action):
    """
    Completion of the processing a single request
    """

    def __init__(self, subject):
        self._subject = subject

    def fire(self):
        self._subject.complete()

    def __str__(self):
        return "%s ending processing" % self._subject.identifier


class StartProcessing(Action):

    def __init__(self, subject):
        self._subject = subject

    def fire(self):
        self._subject.start_processing()

    def __str__(self):
        return "Starting processing"


class Retry(Action):

    def __init__(self, request, back_end):
        self._request = request
        self._back_end = back_end

    def fire(self):
        self._back_end.meter.new_request()
        self._request.send_to(self._back_end.endpoint)

    def __str__(self):
        return "retrying request"


class ProcessingUnit(Agent):
    """
    Represent a single processing unit, i.e., a "server" in queueing systems parlance
    """

    COUNTER = 0

    def __init__(self, server):
        ProcessingUnit.COUNTER += 1
        super().__init__("Unit %d" % ProcessingUnit.COUNTER)
        self._server = server
        self._destination = {}
        self._request = None
        self._stopped = False

    @property
    def service_time(self):
        return self._server.service_time

    def process(self):
        if not self._server.queue.is_empty:
            self.log("Request assigned to %s" % self.identifier)
            self._request = self._server.queue.take()
            if len(self._server.back_ends) > 0:
                self.schedule_in(StartProcessing(self), self.service_time)
            else:
                self.schedule_in(Completion(self), self.service_time)

    def start_processing(self):
        self.log("Requesting %d back-ends" % len(self._server.back_ends))
        for each_back_end in self._server.back_ends:
            self.log("Sending request to %s" % each_back_end.endpoint.identifier)
            request = Request(self)
            self._destination[request] = each_back_end
            each_back_end.meter.new_request()
            request.send_to(each_back_end.endpoint)

    def on_completion_of(self, request):
        self.log("request successful")
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
        self.log("Stopping")
        self._stopped = True
        if self.is_idle:
            self._server.destroy_unit(self)

    def on_rejection_of(self, request):
        self.log("request rejected")
        self._destination[request].back_off.new_rejection()
        retry = Retry(request, self._destination[request])
        self.schedule_in(retry, self._destination[request].back_off.delay)

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




