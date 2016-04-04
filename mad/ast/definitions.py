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


from mad.ast.commons import Expression


class Definition(Expression):
    """
    Abstract definition that binds a name to an expression to be evaluated
    """

    def __init__(self, name, body):
        super().__init__()
        self.name = name
        self.body = body

    def accept(self, evaluation):
        raise NotImplementedError("Definition::accept is abstract!")


class DefineService(Definition):
    """
    Definition of a service and the operations it exposes
    """

    def __init__(self, name, body):
        super().__init__(name, body)

    def accept(self, evaluation):
        return evaluation.of_service_definition(self)

    def __repr__(self):
        return "DefineService(%s, %s)" % (self.name, self.body)


class DefineOperation(Definition):
    """
    Define an operation exposed by a service.
    """

    def __init__(self, name, body):
        super().__init__(name, body)
        self.parameters = []

    def accept(self, evaluation):
        return evaluation.of_operation_definition(self)

    def __repr__(self):
        return "DefineOperation(%s, %s)" % (self.name, str(self.body))


class DefineClientStub(Definition):
    """
    Define a client stub, that is an entity that emits requests at a given frequency
    """

    def __init__(self, name, period, body):
        super().__init__(name, body)
        self.period = period

    def __repr__(self):
        return "DefineClientStub(%d, %s)" % (self.period, self.body)

    def accept(self, evaluation):
        return evaluation.of_client_stub_definition(self)
