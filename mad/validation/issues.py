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


class SemanticIssue:
    """
    Commonalities between all semantic errors
    """
    ERROR = 0
    WARNING = 1

    def __init__(self, level):
        self.level = level

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_error(self):
        return self.level == self.ERROR

    def is_warning(self):
        return self.level == self.WARNING

    def accept(self, visitor):
        raise NotImplementedError("SemanticIssue::accept is abstract")


class ServiceIssue(SemanticIssue):

    def __init__(self, level, service):
        super().__init__(level)
        self.service = service

    def accept(self, visitor):
        raise NotImplementedError("ServiceIssue::accept is abstract")


class EmptyService(ServiceIssue):

    def __init__(self, service):
        super().__init__(self.ERROR, service)

    def accept(self, visitor):
        visitor.empty_service(self)


class UnknownService(ServiceIssue):

    def __init__(self, missing_service):
        super().__init__(self.ERROR, missing_service)

    def accept(self, visitor):
        visitor.unknown_service(self)


class DuplicateIdentifier(SemanticIssue):

    def __init__(self, identifier):
        super().__init__(self.ERROR)
        self.identifier = identifier

    def accept(self, visitor):
        visitor.duplicate_identifier(self)


class OperationIssue(ServiceIssue):

    def __init__(self, level, service, operation):
        super().__init__(level, service)
        self.operation = operation

    def accept(self, visitor):
        raise NotImplementedError("OperationIssue::accept is abstract")


class UnknownOperation(OperationIssue):

    def __init__(self, service, missing_operation):
        super().__init__(self.ERROR, service, missing_operation)

    def accept(self, visitor):
        visitor.unknown_operation(self)


class NeverInvokedOperation(OperationIssue):

    def __init__(self, service, operation):
        super().__init__(self.WARNING, service, operation)

    def accept(self, visitor):
        visitor.never_invoked_operation(self)


class DuplicateOperation(OperationIssue):

    def __init__(self, service, operation):
        super().__init__(self.ERROR, service, operation)

    def accept(self, visitor):
        visitor.duplicate_operation(self)

    def __repr__(self):
        return "Duplicate operation {0.service}::{0.operation}".format(self)
