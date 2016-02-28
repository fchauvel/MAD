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

from mad.des2.environment import Environment


class Symbols:
    SELF = "!self"
    REQUEST = "!request"


class Interpreter:

    def __init__(self, environment=None):
        self.environment = environment or Environment()

    def evaluation_of(self, expression, continuation):
        return Evaluation(self.environment, expression, continuation)

    def evaluate(self, expression):
        return Evaluation(self.environment, expression, self.done).result

    def done(self, result):
        return result


class Evaluation:

    def __init__(self, environment, expression, continuation):
        self.environment = environment
        self.expression = expression
        self.continuation = continuation
        self.results = []

    def __call__(self, *args, **kwargs):
        self.results = args
        return self.expression.accept(self)

    @property
    def result(self):
        return self(None)

    def of_service_definition(self, definition):
        service_environment = self.environment.create_local_environment()
        Interpreter(service_environment).evaluate(definition.body)
        service = Service(service_environment)
        self.environment.define(definition.name, service)
        self.continuation(service)

    def of_operation_definition(self, definition):
        operation = Operation(
            definition.parameters,
            definition.body,
            self.environment
        )
        self.environment.define(definition.name, operation)
        self.continuation(operation)

    def of_client_stub_definition(self, definition):
        client_environment = self.environment.create_local_environment()
        client = ClientStub(client_environment, definition.period, definition.body)
        client.initialize()
        return client

    def of_sequence(self, sequence):
        interpreter = Interpreter(self.environment)

        def switch(result):
            if result == Request.OK:
                return interpreter.evaluation_of(sequence.rest, self.continuation).result
            else:
                return Request.ERROR

        return interpreter.evaluation_of(sequence.first_expression, switch).result

    def of_trigger(self, trigger):
        sender = self.environment.look_up(Symbols.SELF)
        recipient = self.environment.look_up(trigger.service)
        request = Request(sender, trigger.service, sender.on_success, sender.on_error)
        request.send_to(recipient)
        self.continuation(Request.OK)

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
        return None

    def of_think(self, think):
        def resume():
            self.continuation(Request.OK)
        self.environment.schedule().after(think.duration, resume)
        return None


class Operation:

    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.environment = environment

    def __repr__(self):
        return "operation:%s" % (str(self.body))

    def invoke(self, request, arguments):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.REQUEST, request)
        environment.define_each(self.parameters, arguments)

        def send_response(status):
            request.reply(status)
            return status

        result = Interpreter(environment).evaluation_of(self.body, send_response).result
        return result


class Service:

    def __init__(self, environment):
        self.environment = environment
        self.environment.define(Symbols.SELF, self)
        pass

    def process(self, request):
        operation = self.environment.look_up(request.operation)
        operation.invoke(request, [])

    def on_success(self, request):
        pass

    def on_error(self, request):
        pass


class ClientStub:

    def __init__(self, environment, period, body):
        self.environment = environment
        self.environment.define(Symbols.SELF, self)
        self.period = period
        self.body = body

    def initialize(self):
        self.environment.schedule().every(self.period, self.activate)

    def activate(self):
        Interpreter(self.environment).evaluate(self.body)

    def on_success(self, request):
        pass

    def on_error(self, request):
        pass


class Request:
    OK = 1
    ERROR = 1

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


