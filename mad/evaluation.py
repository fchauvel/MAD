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

from random import random

from mad.ast.settings import Settings


class Symbols:
    AUTOSCALING = "!autoscaling"
    LISTENER = "!listener"
    LOGGER = "!logger"
    MONITOR = "!monitor"
    SELF = "!self"
    SERVICE = "!service"
    SIMULATION = "!simulation"
    TASK = "!request"
    THROTTLING = "!throttling"
    QUEUE = "!queue"
    WORKER = "!worker"


class SimulationFactory:
    """
    Interface used to build the simulation entities without depending directly on the constructors.
    Permit to break the circular dependency between Evaluation and Simulation
    """

    def create_service(self, name, environment):
        self._abort(self.create_service.__name__)

    def create_listener(self):
        self._abort(self.create_listener.__name__)

    def create_monitor(self, period):
        self._abort(self.create_monitor.__name__)

    def create_logger(self, environment):
        self._abort(self.create_logger.__name__)

    def create_FIFO_task_pool(self, environment):
        self._abort(self.create_FIFO_task_pool.__name__)

    def create_LIFO_task_pool(self, environment):
        self._abort(self.create_LIFO_task_pool.__name__)

    def create_autoscaler(self, environment, strategy):
        self._abort(self.create_autoscaler.__name__)

    def create_backoff(self, delay):
        self._abort(self.create_backoff.__name__)

    def create_operation(self, environment, definition):
        self._abort(self.create_operation.__name__)

    def create_client_stub(self, environment, definition):
        self._abort(self.create_client_stub.__name__)

    def create_request(self, sender, kind, operation, priority, on_accept=lambda:None, on_reject=lambda:None, on_success=lambda: None, on_error=lambda: None):
        self._abort(self.create_request.__name__)

    def create_no_throttling(self, environment, task_pool):
        self._abort(self.create_no_throttling.__name__)

    def create_tail_drop(self, environment, capacity, task_pool):
        self._abort(self.create_tail_drop.__name__)

    def _abort(self, caller_name):
        raise NotImplementedError("Method '%s::%s' is abstract and must not be directly called!" % (self.__class__.__name__, caller_name))


class Evaluation:
    """
    Represent the future evaluation of an expression within a given environment. The expression is bound to
    a continuation, that is the next evaluation to carry out.
    """

    def __init__(self, environment, expression, factory, continuation=lambda x: x):
        self.environment = environment
        self.expression = expression
        assert callable(continuation), "Continuations must be callable!"
        self.continuation = continuation
        self.simulation = self.environment.look_up(Symbols.SIMULATION)
        self.factory = factory;

    def _look_up(self, symbol):
        return self.environment.look_up(symbol)

    def _define(self, symbol, value):
        self.environment.define(symbol, value)

    def _evaluation_of(self, expression, continuation=lambda x: None):
        return Evaluation(self.environment, expression, self.factory, continuation).result

    @property
    def result(self):
        return self.expression.accept(self)

    def of_service_definition(self, service):
        service_environment = self.environment.create_local_environment()
        service_environment.define(Symbols.LISTENER, self.factory.create_listener())
        Evaluation(service_environment, Settings(), self.factory).result
        Evaluation(service_environment, service.body, self.factory).result
        service = self.factory.create_service(service.name, service_environment)
        self._define(service.name, service)
        monitor = self.factory.create_monitor(Symbols.MONITOR, service_environment, None)
        self._define(Symbols.MONITOR, monitor)
        logger = self.factory.create_logger(service_environment)
        self._define(Symbols.LOGGER, logger)
        return self.continuation(Success(service))

    def of_settings(self, settings):
        self._evaluation_of(settings.queue)
        self._evaluation_of(settings.throttling)
        self._evaluation_of(settings.autoscaling)
        return self.continuation(Success(None))

    def of_fifo(self, fifo):
        queue = self.factory.create_FIFO_task_pool(self.environment)
        self._define(Symbols.QUEUE, queue)
        return self.continuation(Success(None))

    def of_lifo(self, lifo):
        queue = self.factory.create_LIFO_task_pool(self.environment)
        self._define(Symbols.QUEUE, queue)
        return self.continuation(Success(None))

    def of_autoscaling(self, autoscaling):
        autoscaler = self.factory.create_autoscaler(self.environment, autoscaling)
        self._define(Symbols.AUTOSCALING, autoscaler)
        return self.continuation(Success(None))

    def of_tail_drop(self, definition):
        task_pool = self._look_up(Symbols.QUEUE)
        tail_drop = self.factory.create_tail_drop(self.environment, definition.capacity, task_pool)
        self._define(Symbols.QUEUE, tail_drop)
        return self.continuation(Success(None))

    def of_no_throttling(self, no_throttling):
        task_pool = self._look_up(Symbols.QUEUE)
        no_throttling = self.factory.create_no_throttling(self.environment, task_pool)
        self._define(Symbols.QUEUE, no_throttling)
        return self.continuation(Success(None))

    def of_operation_definition(self, operation_definition):
        operation = self.factory.create_operation(self.environment, operation_definition)
        self.environment.define(operation_definition.name, operation)
        return self.continuation(Success(operation))

    def of_client_stub_definition(self, definition):
        client_environment = self.environment.create_local_environment()
        client_environment.define(Symbols.LISTENER, self.factory.create_listener())
        client = self.factory.create_client_stub(client_environment, definition)
        self._define(definition.name, client)
        client.initialize()
        logger = self.factory.create_logger(client_environment)
        self._define(Symbols.LOGGER, logger)
        return self.continuation(Success(client))

    def of_sequence(self, sequence):
        def abort_on_error(previous):
            if previous.is_successful:
                return self._evaluation_of(sequence.rest, self.continuation)
            else:
                return self.continuation(previous)
        return self._evaluation_of(sequence.first_expression, abort_on_error)

    def of_trigger(self, trigger):
        return self._get_busy_for(
            duration=1,
            after=lambda status: self._do_trigger(trigger))

    def of_query(self, query):
        return self._get_busy_for(
            duration=1,
            after=lambda status: self._send_query(query))

    def of_think(self, think):
        """
        Simulate the worker processing the task for the specified amount of time.
        The worker is not released and the task is not paused.
        """
        return self._get_busy_for(
            duration=think.duration,
            after=lambda status: self.continuation(status))

    def of_fail(self, fail):
        if random() < fail.probability:
            return self.continuation(Error())
        else:
            return self.continuation(Success(None))

    def of_retry(self, retry):
        task = self._look_up(Symbols.TASK)
        sender = self._look_up(Symbols.SELF)
        backoff = self.factory.create_backoff(retry.delay)

        def retry_on_error(remaining_tries):
            if remaining_tries <= 0:
                return lambda s: self.continuation(Error())
            else:
                def continuation(status):
                    if status.is_successful:
                        return self.continuation(Success(None))
                    else:
                        def try_again(worker):
                            self.environment.dynamic_scope = worker.environment
                            self._evaluation_of(retry.expression, retry_on_error(remaining_tries-1))

                        task.resume = try_again
                        delay = backoff.delay(retry.limit - remaining_tries)
                        sender.schedule.after(delay, lambda: sender.activate(task))
                        return self._pause()

                return continuation

        return self._evaluation_of(retry.expression, retry_on_error(retry.limit-1))

    def of_ignore_error(self, ignore_error):
        def ignore_status(status):
            return self.continuation(Success(status.value))
        return self._evaluation_of(ignore_error.expression, ignore_status)

    def _do_trigger(self, trigger):
        task = self._look_up(Symbols.TASK)
        sender = self._look_up(Symbols.SELF)
        recipient = self._look_up(trigger.service)

        def on_reject():
            # TODO: Notify rejection received!

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Error())

            task.resume = resume
            sender.activate(task)

        def on_accept():
            # TODO: Notify acceptance ack received!

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Success())

            task.resume = resume
            sender.activate(task)

        # TODO: Replace that ugly magic '1'
        request = self.factory.create_request(
            sender,
            1,
            trigger.operation,
            trigger.priority,
            on_accept= on_accept,
            on_reject= on_reject)

        sender.listener.posting_of(trigger.service, request)
        request.send_to(recipient)

        return self._pause()

    def _send_query(self, query):
        task = self._look_up(Symbols.TASK)
        sender = self._look_up(Symbols.SELF)
        recipient = self._look_up(query.service)

        def on_reject():
            # TODO: Notify rejection received!

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Error())

            task.resume = resume
            sender.activate(task)

        def on_success():
            sender.listener.success_of(request)

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Success())

            task.resume = resume
            sender.activate(task)

        def on_error():
            sender.listener.failure_of(request)

            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Error())

            task.resume = resume
            sender.activate(task)

        # TODO: Replace that ugly magic '0'
        request = self.factory.create_request(
            sender,
            0,
            query.operation,
            query.priority,
            on_reject=on_reject,
            on_success=on_success,
            on_error=on_error)

        sender.listener.posting_of(query.service, request)
        request.send_to(recipient)

        def timeout_check():
            def resume(worker):
                self.environment.dynamic_scope = worker.environment
                self.continuation(Error())

            if request.is_pending:
                sender.listener.timeout_of(request)
                request.discard()
                task.resume = resume
                sender.activate(task)

        if query.has_timeout:
            sender.schedule.after(query.timeout, timeout_check)

        return self._pause()

    def _get_busy_for(self, duration, after):
        self.simulation.schedule.after(duration, lambda: after(Success()))
        return Busy()

    def _pause(self):
        service = self._look_up(Symbols.SELF)
        task = self._look_up(Symbols.TASK)
        worker = self.environment.dynamic_look_up(Symbols.WORKER)
        service.pause(task)
        service.release(worker)
        return Paused()


class Result:
    """
    Represent the result of an evaluation, including the status (pass, failed) and the value if associated value if any
    """
    PAUSED = 0
    SUCCESS = 1
    ERROR = 2
    BUSY = 3

    def __init__(self, status, value):
        self.status = status
        self.value = value

    @property
    def is_successful(self):
        return self.status == Result.SUCCESS

    @property
    def is_paused(self):
        return self.status == Result.PAUSED

    @property
    def is_erroneous(self):
        return self.status == Result.ERROR

    def is_busy(self):
        return self.status == Result.BUSY

    names = {ERROR: "ERROR",
             BUSY: "BUSY",
             PAUSED: "PAUSED",
             SUCCESS: "SUCCESS"}

    def __repr__(self):
        return self.names[self.status]


class Success(Result):

    def __init__(self, value=None):
        super().__init__(Result.SUCCESS, value)


class Error(Result):

    def __init__(self):
        super().__init__(Result.ERROR, None)


class Paused(Result):
    def __init__(self):
        super().__init__(Result.PAUSED, None)


class Busy(Result):
    def __init__(self):
        super().__init__(Result.BUSY, None)
