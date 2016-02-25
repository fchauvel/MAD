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


class DefineService:

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def accept(self, simulator):
        simulator.evaluate_service_definition(self)


class Generator:

    def __init__(self, behaviour):
        self.behaviour = behaviour

    def accept(self, simulator):
        simulator.evaluate_generator_definition(self)

class At:

    def __init__(self, time, behaviour):
        self.time = time
        self.behaviour = behaviour


class DefineOperation:

    def __init__(self, name, body):
        self.name = name
        self.parameters = []
        self.body = body

    def accept(self, simulator):
        return simulator.evaluate_operation_definition(self)


class Trigger:

    def __init__(self, service, operation):
        self.service = service
        self.operation = operation

    def accept(self, simulator):
        simulator.evaluate_trigger(self)


class Sequence:

    def __init__(self, *args, **kwargs):
        self.body = args

    def accept(self, simulator):
        return simulator.evaluate_sequence(self)