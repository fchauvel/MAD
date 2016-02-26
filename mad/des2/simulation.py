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

    def __call__(self, *args, **kwargs):
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
        return interpreter.evaluation_of(
                sequence.first_expression,
                interpreter.evaluation_of(sequence.rest, self.continuation)
        ).result

    def of_trigger(self, trigger):
        service = self.environment.look_up(trigger.service)
        service.process(Request(trigger.operation))
        self.continuation(None)

    def of_query(self, query):
        service = self.environment.look_up(query.service)
        request = Request(
                query.operation,
        #        on_response = self.continuation
        )
        service.process(request)
        self.continuation(None)

    def of_think(self, think):
        def resume():
            self.continuation(None)
        self.environment.schedule().after(think.duration, resume)
        return None


class Operation:

    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.environment = environment

    def __repr__(self):
        return "operation:%s" % (str(self.body))

    def invoke(self, arguments):
        environment = self.environment.create_local_environment()
        environment.define_each(self.parameters, arguments)
        return Interpreter(environment).evaluate(self.body)


class Service:

    def __init__(self, environment):
        self.environment = environment
        pass

    def process(self, request):
        operation = self.environment.look_up(request.operation)
        operation.invoke([])


class ClientStub:

    def __init__(self, environment, period, body):
        self.environment = environment
        self.period = period
        self.body = body

    def initialize(self):
        self.environment.schedule().every(self.period, self.activate)

    def activate(self):
        Interpreter(self.environment).evaluate(self.body)


class Request:

    def __init__(self, operation):
        self.operation = operation
