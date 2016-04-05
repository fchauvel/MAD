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


class SymbolTable:

    def __init__(self):
        self.services = {}
        self._current_service = None

    def open_service(self, service):
        self.services[service.name] = []
        self._current_service = self.services[service.name]

    def close_service(self):
        self._current_service = None

    def add_operation(self, operation):
        self._current_service.append(operation.name)

    def miss_service(self, service):
        return service not in self.services

    def miss_operation(self, service, operation):
        return (service, operation) not in self.services.items()


class Validator:
    "Traverse the AST searching for inconsistencies, so called 'Semantic Errors'"

    def __init__(self, expression):
        self.checks = []
        self.errors = []
        self.symbols = SymbolTable()
        expression.accept(self)
        for each_check in self.checks:
            each_check(self.symbols)

    def of_service_definition(self, service):
        self.symbols.open_service(service)
        service.body.accept(self)
        self.symbols.close_service()

    def of_operation_definition(self, operation):
        self.symbols.add_operation(operation)
        operation.body.accept(self)

    def of_client_stub_definition(self, client):
        client.body.accept(self)

    def of_trigger(self, trigger):
        self._check_is_defined(trigger.service)
        self._check_has_operation(trigger.service, trigger.operation)

    def of_think(self, think):
        pass

    def of_sequence(self, sequence):
        for each_expression in sequence.body:
            each_expression.accept(self)

    def _check_is_defined(self, service):
        def check(symbols):
            if symbols.miss_service(service):
                error = UnknownService(service)
                self._record(error)
        self.checks.append(check)

    def _record(self, error):
        self.errors.append(error)

    def _check_has_operation(self, service, operation):
        def check(symbols):
            if symbols.miss_operation(service, operation):
                error = UnknownOperation(service, operation)
                self._record(error)
        self.checks.append(check)


class SemanticError:
    """
    Commonalities between all semantic errors
    """

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class UnknownService(SemanticError):

    def __init__(self, missing_service):
        super().__init__()
        self.service = missing_service


class UnknownOperation(SemanticError):

    def __init__(self, service, missing_operation):
        super().__init__()
        self.service = service
        self.operation = missing_operation