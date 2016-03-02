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
        service = Service(definition.name, service_environment)
        self.environment.define(definition.name, service)
        return self.continuation(Success(service))

    def of_operation_definition(self, definition):
        operation = Operation(
            definition.name,
            definition.parameters,
            definition.body,
            self.environment
        )
        self.environment.define(definition.name, operation)
        return self.continuation(Success(operation))

    def of_client_stub_definition(self, definition):
        client_environment = self.environment.create_local_environment()
        client = ClientStub(definition.name, client_environment, definition.period, definition.body)
        client.initialize()
        return self.continuation(Success(client))

    def of_sequence(self, sequence):
        def switch(status):
            if status.is_successful:
                return Evaluation(self.environment, sequence.rest, self.continuation).result
            else:
                return self.continuation(status)
        return Evaluation(self.environment, sequence.first_expression, switch).result

    def of_trigger(self, trigger):
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(trigger.service)
        request = Request(sender, trigger.service)
        request.send_to(recipient)
        return self.continuation(Success(None))

    def of_query(self, query):
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(query.service)
        request = Request(
                sender,
                query.operation,
                on_success= lambda: self.continuation(Success()),
                on_error= lambda: self.continuation(Error())
        )
        self.environment.log().record(self.environment.schedule().time_now, sender.name, "Sending Req. %d to %s::%s" % (request.identifier, query.service, query.operation))
        request.send_to(recipient)
        return Success(None)

    def of_think(self, think):
        def resume():
            self.continuation(Success())
        self.environment.schedule().after(think.duration, resume)
        return Success()

    def of_retry(self, retry):
        def do_retry(count):
            if count == 0:
                return Error()
            else:
                status = Evaluation(self.environment, retry.expression).result
                if status.is_successful:
                    return self.continuation(status)
                else:
                    return do_retry(count-1)

        return do_retry(retry.limit)

    def of_ignore_error(self, ignore_error):
        def ignore_status(status):
            return self.continuation(Success(status.value))
        return Evaluation(self.environment, ignore_error.expression, ignore_status).result


class Result:
    """
    Represent the result of an evaluation, including the status (pass, failed) and the value if associated value if any
    """
    SUCCESS = 1
    ERROR = 2

    def __init__(self, status, value):
        self.status = status
        self.value = value

    @property
    def is_successful(self):
        return self.status == Result.SUCCESS

    def __repr__(self):
        return "SUCCESS" if (self.is_successful) else "ERROR"


class Success(Result):

    def __init__(self, value=None):
        super().__init__(Result.SUCCESS, value)


class Error(Result):

    def __init__(self):
        super().__init__(Result.ERROR, None)


class SimulatedEntity:
    """
    Factor out commonalities between all simulated entities
    """

    def __init__(self, name, environment):
        self.environment = environment
        self.name = name

    @property
    def schedule(self):
        return self.environment.schedule()

    def log(self, message, values):
        now = self.environment.schedule().time_now
        caller = self.environment.look_up(Symbols.SELF)
        self.environment.log().record(now, caller.name, message % values)

    def look_up(self, symbol):
        return self.environment.look_up(symbol)


class Operation(SimulatedEntity):

    def __init__(self, name, parameters, body, environment):
        super().__init__(name, environment)
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return "operation:%s" % (str(self.body))

    def invoke(self, request, arguments, continuation=lambda r: r):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.REQUEST, request)
        environment.define_each(self.parameters, arguments)

        def send_response(status):
            self.log("Reply to Req. %d (%s)", (request.identifier, str(status)))
            request.reply(status)
            continuation(status)

        Evaluation(environment, self.body, send_response).result


class Service(SimulatedEntity):

    def __init__(self, name, environment):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.pending_requests = RequestPool()
        self.workers = WorkerPool([ self._new_worker() ])

    def _new_worker(self):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.SERVICE, self)
        return Worker(environment)

    def process(self, request):
        self.log("Req. %d accepted", request.identifier)
        if self.workers.are_available:
            worker = self.workers.acquire_one()
            worker.assign(request)
        else:
            self.pending_requests.put(request)

    def worker_idle(self, worker):
        if self.pending_requests.is_empty:
            self.workers.release(worker)
        else:
            request = self.pending_requests.take()
            worker.assign(request)


class WorkerPool:

    def __init__(self, workers):
        self.idle_workers = workers

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
        self.idle_workers.append(worker)


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


class ClientStub(SimulatedEntity):

    def __init__(self, name, environment, period, body):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.period = period
        self.body = body

    def initialize(self):
        self.schedule.every(self.period, self.activate)

    def activate(self):
        Evaluation(self.environment, self.body).result

    def on_success(self, request):
        self.log("Req. %d complete", request.identifier)

    def on_error(self, request):
        self.log("Req. %d failed", request.identifier)


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


class Status:
    SUCCESS = 1
    ERROR = 2
    WAITING = 3


class Request:

    def __init__(self, sender, operation, on_success=None, on_error=None):
        assert sender, "Invalid sender (found %s)" % str(sender)
        self.identifier = sender.environment.next_request_id()
        self.sender = sender
        self.operation = operation
        self.handlers = {
            Status.SUCCESS: [lambda: self.sender.on_success(self)],
            Status.ERROR: [lambda: self.sender.on_error(self)]
        }
        if on_success: self.handlers.get(Status.SUCCESS).append(on_success)
        if on_error: self.handlers.get(Status.ERROR).append(on_error)

    def send_to(self, service):
        service.process(self)

    def reply(self, status):
        for each_handler in self.handlers.get(status.status):
            each_handler()


