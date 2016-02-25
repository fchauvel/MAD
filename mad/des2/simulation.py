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

class Simulator:

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return Simulation()


class Simulation:

    def __init__(self, environment=Environment()):
        self.environment = environment

    def until(self, limit):
        return self

    @property
    def services(self):
        class FakeService:

            @property
            def called_once(self):
                return True

        return {"my_service": FakeService()}

    def evaluate(self, expression):
        return expression.accept(self)

    def evaluate_service_definition(self, definition):
        service_environment = self.environment.create_local_environment()
        Simulation(service_environment).evaluate(definition.body)
        service = Service(service_environment)
        self.environment.define(definition.name, service)

    def evaluate_operation_definition(self, definition):
        operation = Operation(
            definition.parameters,
            definition.body,
            self.environment
        )
        self.environment.define(definition.name, operation)
        return operation

    def evaluate_sequence(self, sequence):
        result = None
        for each_expression in sequence.body:
            result = self.evaluate(each_expression)
        return result

    def evaluate_trigger(self, trigger):
        service = self.environment.look_up(trigger.service)
        service.process(Request(trigger.operation))
        return None


# To evaluate 'invoke operation X'
# 1. Evaluate the arguments of the invocation
# 2. Spawn the current operation environment as new-env
# 3. Evaluate the body of the function in the new-env

class Operation:

    def __init__(self, parameters, body, environment):
        self.parameters = parameters
        self.body = body
        self.environment = environment

    def invoke(self, arguments):
        environment = self.environment.create_local_environment()
        for (symbol, value) in zip(self.parameters, arguments):
            environment.define(symbol, value)
        return Simulation(environment).evaluate(self.body)


class Service:

    def __init__(self, environment):
        self.environment = environment
        pass

    def process(self, request):
        operation = self.environment.look_up(request.operation)
        operation.invoke([])


class Request:

    def __init__(self, operation):
        self.operation = operation

