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

from mad.validation.issues import *


class Operation:

    def __init__(self, name):
        self.name = name
        self.invocation_count = 0

    def invoke(self):
        self.invocation_count += 1

    def is_not_invoked(self):
        return self.invocation_count == 0


class Service:

    def __init__(self, name):
        self.name = name
        self.operations = {}

    def add_operation(self, name):
        self.operations[name] = Operation(name)


class SymbolTable:

    def __init__(self):
        self.services = {}
        self._current_service = None

    @property
    def service(self):
        assert self._current_service, "No service currently opened!"
        return self.services[self._current_service]

    def open_service(self, service):
        assert not self._current_service, "Service '%s' currently opened!" % self._current_service
        if service.name in self.services:
            raise ValueError("Duplicated Service")
        self.services[service.name] = Service(service.name)
        self._current_service = service.name

    def close_service(self):
        assert self._current_service, "No service currently opened!"
        self._current_service = None

    def add_operation(self, operation):
        if operation.name in self.service.operations:
            raise ValueError("Duplicate operation")
        self.service.add_operation(operation.name)

    def miss_service(self, service):
        return service not in self.services

    def miss_operation(self, service, operation):
        return not (service in self.services and
                    operation in self.services[service].operations)

    def invoke(self, service, operation):
        if service in self.services and \
           operation in self.services[service].operations:
            self.services[service].operations[operation].invoke()

    def never_invoked(self, service, operation):
        return self.services[service].operations[operation].is_not_invoked()


class InvalidModel(Exception):

    def __init__(self, issues):
        self.issues = issues


class Validator:
    "Traverse the AST searching for inconsistencies, so called 'Semantic Errors'"

    def __init__(self):
        self.checks = []
        self.errors = []
        self.symbols = SymbolTable()

    def validate(self, expression):
        expression.accept(self)
        for each_check in self.checks:
            each_check(self.symbols)
        if self._has_any_error():
            raise InvalidModel(self.errors)

    def _has_any_error(self):
        for any_issue in self.errors:
            if any_issue.is_error():
                return True
        return False

    def raised_warnings(self):
        for any_issue in self.errors:
            if any_issue.is_warning():
                return True
        return False

    def of_service_definition(self, service):
        try:
            self.symbols.open_service(service)
            service.body.accept(self)
            self._check_has_at_least_one_operation(service)
            self.symbols.close_service()
        except ValueError:
            error = DuplicateService(service.name)
            self._report(error)

    def of_operation_definition(self, operation):
        try:
            self.symbols.add_operation(operation)
            operation.body.accept(self)
            self._check_is_invoked(self.symbols.service.name, operation.name)
        except ValueError:
            error = DuplicateOperation(self.symbols.service.name, operation.name)
            self._report(error)

    def of_client_stub_definition(self, client):
        client.body.accept(self)

    def of_trigger(self, trigger):
        self.symbols.invoke(trigger.service, trigger.operation)
        self._check_is_defined(trigger.service)
        self._check_has_operation(trigger.service, trigger.operation)

    def of_query(self, query):
        self.symbols.invoke(query.service, query.operation)
        self._check_is_defined(query.service)
        self._check_has_operation(query.service, query.operation)

    def of_think(self, think):
        pass

    def of_sequence(self, sequence):
        for each_expression in sequence.body:
            each_expression.accept(self)

    def of_settings(self, settings):
        pass

    def _check_is_defined(self, service):
        def check(symbols):
            if symbols.miss_service(service):
                error = UnknownService(service)
                self._report(error)
        self.checks.append(check)

    def _check_has_at_least_one_operation(self, service):
        def check(symbols):
            if len(symbols.services[service.name].operations) == 0:
                error = EmptyService(service.name)
                self._report(error)
        self.checks.append(check)

    def _check_is_invoked(self, service, operation):
        def check(symbols):
            if symbols.never_invoked(service, operation):
                warning = NeverInvokedOperation(service, operation)
                self._report(warning)
        self.checks.append(check)

    def _check_has_operation(self, service, operation):
        def check(symbols):
            if symbols.miss_operation(service, operation):
                error = UnknownOperation(service, operation)
                self._report(error)
        self.checks.append(check)

    def _report(self, error):
        self.errors.append(error)
