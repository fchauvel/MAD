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

    def accept(self, evaluation):
        return evaluation.of_service_definition(self)

    def __repr__(self):
        return "Service(%s, %s)" % (self.name, self.body)


class DefineOperation:

    def __init__(self, name, body):
        self.name = name
        self.parameters = []
        self.body = body

    def accept(self, evaluation):
        return evaluation.of_operation_definition(self)

    def __repr__(self):
        return "Operation(%s, %s)" % (self.name, str(self.body))


class Trigger:

    def __init__(self, service, operation):
        self.service = service
        self.operation = operation

    def accept(self, evaluation):
        return evaluation.of_trigger(self)

    def __repr__(self):
        return "Trigger(%s, %s)" % (self.service, self.operation)


class Query:

    def __init__(self, service, operation):
        self.service = service
        self.operation = operation

    def accept(self, evaluation):
        return evaluation.of_query(self)

    def __repr__(self):
        return "Query(%s, %s)" % (self.service, self.operation)


class Think:

    def __init__(self, duration):
        self.duration = duration

    def accept(self, evaluation):
        return evaluation.of_think(self)

    def __repr__(self):
        return "Think(%d)" % self.duration


class Sequence:

    def __init__(self, *args, **kwargs):
        self.body = args

    @property
    def first_expression(self):
        return self.body[0]

    @property
    def rest(self):
        if len(self.body) > 2:
            return Sequence(self.body[1:])
        else:
            return self.body[1]

    def accept(self, evaluation):
        return evaluation.of_sequence(self)

    def __repr__(self):
        body = [str(each_expression) for each_expression in self.body]
        return "Sequence(%s)" % ", ".join(body)