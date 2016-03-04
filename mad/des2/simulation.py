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
        self.results = args # TODO: remove this line
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
        task = self.environment.look_up(Symbols.TASK)
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(query.service)

        def on_success():
            sender.log("Req. %d complete", request.identifier)

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Success())

            task.resume = resume
            sender.activate(task)

        def on_error():
            sender.log("Req. %d failed", request.identifier)

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Error())

            task.resume = resume
            sender.activate(task)

        request = Request(sender, query.operation, on_success, on_error)
        sender.log("Sending Req. %d to %s::%s", (request.identifier, query.service, query.operation))
        request.send_to(recipient)

        worker = self.environment.dynamic_look_up(Symbols.WORKER)
        sender.release(worker)
        return Success(None)

    def of_think(self, think):
        def resume():
            self.continuation(Success())
        self.environment.schedule().after(think.duration, resume)
        return Success()

    def of_retry(self, retry):

        def do_retry(remaining_tries):
            if remaining_tries == 0:
                return lambda status: Error()
            else:
                def continuation(status):
                    if status.is_successful:
                        return self.continuation(status)
                    else:
                        return Evaluation(self.environment, retry.expression, do_retry(remaining_tries-1)).result
            return continuation

        return Evaluation(self.environment, retry.expression, do_retry(retry.limit-1)).result

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
        now = self.schedule.time_now
        caller = self.look_up(Symbols.SELF)
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

    def invoke(self, task, arguments, continuation=lambda r: r, worker=None):
        environment = self.environment.create_local_environment(worker.environment)
        environment.define(Symbols.TASK, task)
        environment.define_each(self.parameters, arguments)

        def send_response(status):
            self.log("Reply to Req. %d (%s)", (task.request.identifier, str(status)))
            if status.is_successful:
                task.request.reply_success()
            else:
                task.request.reply_error(status)
            continuation(status)

        Evaluation(environment, self.body, send_response).result


class Service(SimulatedEntity):

    def __init__(self, name, environment):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.pending_requests = RequestPool()
        self.workers = WorkerPool([ self._new_worker(id) for id in range(1, 2) ])

    def _new_worker(self, identifier):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.SERVICE, self)
        return Worker(identifier, environment)

    def process(self, request):
        task = Task(request)
        if self.workers.are_available:
            self.log("Req. %d accepted", request.identifier)
            worker = self.workers.acquire_one()
            worker.assign(task)
        else:
            self.log("Req. %d enqueued", request.identifier)
            self.pending_requests.put(task)

    def release(self, worker):
        if self.pending_requests.is_empty:
            self.workers.release(worker)
        else:
            task = self.pending_requests.take()
            worker.assign(task)

    def activate(self, task):
        if self.workers.are_available:
            worker = self.workers.acquire_one()
            worker.assign(task)
        else:
            self.pending_requests.activate(task)


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


class Task:

    def __init__(self, request=None):
        self.request = request
        self.is_started = False
        self.resume = lambda: None

    def mark_as_started(self):
        self.is_started = True


class ClientStub(SimulatedEntity):

    def __init__(self, name, environment, period, body):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.period = period
        self.body = body

    def initialize(self):
        self.schedule.every(self.period, self.invoke)

    def invoke(self):
        def post_processing(status):
            if status.is_successful:
                self.on_success()
            else:
                self.on_error()
        self.environment.define(Symbols.TASK, Task())
        env = self.environment.create_local_environment(self.environment)
        env.define(Symbols.WORKER, self)
        Evaluation(env, self.body, post_processing).result

    def activate(self, task):
        task.resume(self)

    def release(self, worker):
        pass

    def on_success(self):
        pass

    def on_error(self):
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

    def activate(self, request):
        self.requests.insert(0, request)


class Status:
    SUCCESS = 1
    ERROR = 2
    WAITING = 3


class Request:

    def __init__(self, sender, operation, on_success=lambda: None, on_error=lambda: None):
        assert sender, "Invalid sender (found %s)" % str(sender)
        self.identifier = sender.environment.next_request_id()
        self.sender = sender
        self.operation = operation
        self.on_success = on_success
        self.on_error = on_error

    def send_to(self, service):
        service.process(self)

    def reply_success(self):
        self.on_success()

    def reply_error(self):
        self.on_error()

