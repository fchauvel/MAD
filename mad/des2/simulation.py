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

from mad.des2.environment import Symbols, Environment


class Evaluation:
    """
    Represent the future evaluation of an expression, within a given environment. The expression is bound to
    a continuation, that is the next evaluation to carry out.
    """

    def __init__(self, environment, expression, continuation=lambda x: x):
        self.environment = environment
        self.expression = expression
        assert callable(continuation), "Continuations must be callable!"
        self.continuation = continuation

    def __call__(self, *args, **kwargs):
        self.results = args
        return self.expression.accept(self)

    @property
    def result(self):
        return self(None)

    def of_service_definition(self, definition):
        service_environment = self.environment.create_local_environment()
        Evaluation(service_environment, definition.body).result
        service = Service(service_environment)
        self.environment.define(definition.name, service)
        return self.continuation(service)

    def of_operation_definition(self, definition):
        operation = Operation(
            definition.parameters,
            definition.body,
            self.environment
        )
        self.environment.define(definition.name, operation)
        return self.continuation(operation)

    def of_client_stub_definition(self, definition):
        client_environment = self.environment.create_local_environment()
        client = ClientStub(client_environment, definition.period, definition.body)
        client.initialize()
        return self.continuation(client)

    def of_sequence(self, sequence):
        def switch(result):
            if result == Request.OK:
                Evaluation(self.environment, sequence.rest, self.continuation).result
            else:
                self.continuation(Request.ERROR)
        return Evaluation(self.environment, sequence.first_expression, switch).result

    def of_trigger(self, trigger):
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(trigger.service)
        request = Request(sender, trigger.service, sender.on_success, sender.on_error)
        request.send_to(recipient)
        return self.continuation(Request.OK)

    def of_query(self, query):
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(query.service)
        request = Request(
                sender,
                query.operation,
                on_success= lambda result: sender.on_success(),
                on_error= lambda result: self.continuation(Request.ERROR)
        )
        request.send_to(recipient)
        return Request.WAITING

    def of_think(self, think):
        def resume():
            self.continuation(Request.OK)
        self.environment.schedule().after(think.duration, resume)
        return Request.WAITING


class Operation:

    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.environment = environment

    def __repr__(self):
        return "operation:%s" % (str(self.body))

    def invoke(self, request, arguments, continuation=lambda r: r):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.REQUEST, request)
        environment.define_each(self.parameters, arguments)

        def send_response(status):
            request.reply(status)
            continuation(0)

        Evaluation(environment, self.body, send_response).result


class Service:

    def __init__(self, environment):
        self.environment = environment
        self.environment.define(Symbols.SELF, self)
        self.pending_requests = RequestPool()
        self._make_workers()

    def _make_workers(self):
        self.idle_workers = WorkerPool()
        environment = self.environment.create_local_environment()
        environment.define(Symbols.SERVICE, self)
        new_worker = Worker(environment)
        self.idle_workers.put(new_worker)

    def process(self, request):
        if self.idle_workers.is_empty:
            self.pending_requests.put(request)
        else:
            worker = self.idle_workers.take()
            worker.assign(request)

    def worker_idle(self, worker):
        if self.pending_requests.is_empty:
            self.idle_workers.put(worker)
        else:
            request = self.pending_requests.take()
            worker.assign(request)

    def on_success(self, request):
        pass

    def on_error(self, request):
        pass


class Worker:
    """
    Represent a worker (i.e., a thread, or a service replica) that handles requests
    """

    def __init__(self, environment):
        self.environment = environment

    def assign(self, request):
        def release_worker(result):
            service = self.environment.look_up(Symbols.SERVICE)
            service.worker_idle(self)

        operation = self.environment.look_up(request.operation)
        operation.invoke(request, [], release_worker)


class WorkerPool:

    def __init__(self):
        self.workers = []

    @property
    def size(self):
        return len(self.workers)

    @property
    def is_empty(self):
        return self.size == 0

    def put(self, worker):
        self.workers.append(worker)

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take from an empty worker pool!")
        return self.workers.pop(0)


class ClientStub:

    def __init__(self, environment, period, body):
        self.environment = environment
        self.environment.define(Symbols.SELF, self)
        self.period = period
        self.body = body

    def initialize(self):
        self.environment.schedule().every(self.period, self.activate)

    def activate(self):
        Evaluation(self.environment, self.body, lambda x: x).result

    def on_success(self, request):
        pass

    def on_error(self, request):
        pass


class RequestPool:

    def __init__(self):
        self.requests = []

    def put(self, request):
        self.requests.append(request)

    def take(self):
        if self.is_empty:
            raise ValueError("Cannot take a request from an empty pool!")
        return self.requests.pop(0)

    @property
    def is_empty(self):
        return self.size == 0

    @property
    def size(self):
        return len(self.requests)


class Request:
    OK = 1
    ERROR = 2
    WAITING = 3

    def __init__(self, sender, operation, on_success, on_error):
        assert sender, "Invalid sender (found %s)" % str(sender)
        self.sender = sender
        self.operation = operation

        def default_on_success():
            sender.on_success(self)
        self.on_success = on_success or default_on_success

        def default_on_error():
            sender.on_error(self)
        self.on_error = on_error or default_on_error

    def send_to(self, service):
        service.process(self)

    def reply(self, status):
        if status == Request.OK:
            self.on_success(self)
        else:
            self.on_error(self)


