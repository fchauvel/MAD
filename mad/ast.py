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


class Architecture:
    """
    Root element of the syntax tree. Contains the services and in turn their operation
    """

    def __init__(self, name):
        if not name:
            raise ValueError("Invalid name for architectures (found '%s')" % name)
        self.name = name

    def __repr__(self):
        return "Architecture(%s)" % self.name


class Service:
    """
    The definition of a service, including its configuration and the behaviour of its operations
    """

    def __init__(self, name, operations):
        if not name: raise ValueError("Invalid service name (found '%s'" % name)
        self.name = name

        if not operations: raise ValueError("Services must have at least one operation (None found)")
        self.operations = operations

    def __repr__(self):
        return "Service(%s)" % self.name


class Operation:
    """
    Definition of an operation exposed by a service
    """

    def __init__(self, name, behaviour):
        if not name: raise ValueError("Invalid operation name (found '%s')" % name)
        self.name = name

        if not behaviour: raise ValueError("Invalid operation behaviour (found '%s')" % str(behaviour))
        self.behaviour = behaviour

    def __repr__(self):
        return "Operation(%s)" % self.name


class Action:
    """
    The trigger action, which invoke asynchronously a remote operation
    """

    DEFAULT_TIMEOUT = 10

    def __init__(self, service, operation, timeout):
        if not service: raise ValueError("Invalid service reference (found %s::%s)" % (service, operation))
        self.service = service

        if not operation: raise ValueError("Invalid operation reference (found %s::%s)" % (service, operation))
        self.operation = operation

        if timeout < 0: raise ValueError("Invalid negative timeout value (found %d)" % int(timeout))
        self.timeout = timeout

    def __repr__(self):
        return "Trigger(%s::%s)" % (self.service, self.operation)


class TriggerAction(Action):

    def __init__(self, service, operation, timeout=Action.DEFAULT_TIMEOUT):
        super().__init__(service, operation, timeout)


class RequestAction(Action):

    def __init__(self, service, operation, timeout=Action.DEFAULT_TIMEOUT):
        super().__init__(service, operation, timeout)


class UtilisationRule:
    """
    Scalability policy based on utilisation rules.
    """

    def __init__(self, lower_edge, upper_edge, magnitude):
        self.lower_edge = lower_edge
        self.upper_edge = upper_edge
        self.magnitude = magnitude


class Retry:

    def __init__(self, limit, delay=10):
        if limit < 0: raise ValueError("Illegal negative retry limit (found %d)" % int(limit))
        self.limit = limit

        self.delay = delay

