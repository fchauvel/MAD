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


class Expression:
    """
    Abstract Expression class
    """

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        assert isinstance(other, Expression), "Can only sequence expressions (found '%s')" % type(other)
        if isinstance(other, Sequence):
            content = [self] + other.body
        else:
            content = [self, other]
        return Sequence(*content)

    def accept(self, evaluation):
        raise NotImplementedError("Expression::accept is abstract!")


class Sequence(Expression):
    """
    A sequence of actions (i.e., invocation or think)
    """

    def __init__(self, *args, **kwargs):
        self.body = list(args)

    @property
    def first_expression(self):
        return self.body[0]

    @property
    def rest(self):
        if len(self.body) > 2:
            return Sequence(*self.body[1:])
        else:
            return self.body[1]

    def accept(self, evaluation):
        return evaluation.of_sequence(self)

    def __repr__(self):
        body = [str(each_expression) for each_expression in self.body]
        return "Sequence(%s)" % ", ".join(body)

    def __add__(self, other):
        assert isinstance(other, Expression), "Can only sequence expressions (found '%s')" % type(other)
        if isinstance(other, Sequence):
            content = self.body + other.body
        else:
            content = self.body + [other]
        return Sequence(*content)


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




class QueueDiscipline(Expression):

    def __init__(self):
        super().__init__()

    def accept(self, evaluation):
        raise NotImplementedError("QueueDiscipline::accept is abstract!")


class LIFO(QueueDiscipline):

    def __init__(self):
        super().__init__()

    def accept(self, evaluation):
        return evaluation.of_lifo(self)

    def __repr__(self):
        return "LIFO"


class FIFO(QueueDiscipline):

    def accept(self, evaluation):
        return evaluation.of_fifo(self)

    def __repr__(self):
        return "FIFO"


class Autoscaling(Expression):

    def __init__(self, period=30, limits=(1, 4)):
        super().__init__()
        if not isinstance(period, int):
            raise ValueError("Expecting integer value for period, but found '%1$s' (%2$s)" % (str(period), type(period)))
        self.period = period

        if not isinstance(limits, tuple):
            raise ValueError("Expecting interval (min, max) for limits but found '%1$s'" % str(limits))
        self.limits = limits

    def __repr__(self):
        return "Autoscaling(%1$d, %2$s)" % (self.period, str(self.limits))


class Settings(Expression):

    def __init__(self, queue=FIFO(), autoscaling=Autoscaling()):
        super().__init__()
        self._queue = queue
        self._autoscaling = autoscaling

    @property
    def queue(self):
        return self._queue

    def accept(self, evaluation):
        return evaluation.of_settings(self)

    def __repr__(self):
        return "Settings(queue: %s)" % str(self._queue)


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


class Action(Expression):
    """
    Abstract all action that can be performed within an operation
    """

    def __init__(self):
        super().__init__()

    def accept(self, evaluation):
        raise NotImplementedError("Action::accept(evaluation) is abstract!")


class Invocation(Action):
    """
    Abstract invocation of a remote operation
    """

    def __init__(self, service, operation):
        super().__init__()
        self.service = service
        self.operation = operation

    def accept(self, evaluation):
        raise NotImplementedError("Invocation::accept(evaluation) is abstract!")


class Trigger(Invocation):
    """
    An non-blocking invocation of a remote operation
    """

    def __init__(self, service, operation):
        super().__init__(service, operation)

    def accept(self, evaluation):
        return evaluation.of_trigger(self)

    def __repr__(self):
        return "Trigger(%s, %s)" % (self.service, self.operation)


class Query(Invocation):
    """
    A blocking invocation of a remote operation
    """

    def __init__(self, service, operation):
        super().__init__(service, operation)

    def accept(self, evaluation):
        return evaluation.of_query(self)

    def __repr__(self):
        return "Query(%s, %s)" % (self.service, self.operation)


class Think(Action):
    """
    Simulate a local time-consuming computation
    """

    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def accept(self, evaluation):
        return evaluation.of_think(self)

    def __repr__(self):
        return "Think(%d)" % self.duration


class Retry:
    """
    Retry an action a given number of time
    """

    def __init__(self, expression, limit):
        self.expression = expression
        assert limit > 0, "Retry limit must be strictly positive (found %d)" % limit
        self.limit = limit

    def accept(self, evaluation):
        return evaluation.of_retry(self)

    def __repr__(self):
        return "Retry(%s, %d)" % (str(self.expression), self.limit)


class IgnoreError:
    """
    Ignore error occuring during the evaluation of the given expression
    """

    def __init__(self, expression):
        self.expression = expression

    def accept(self, evaluation):
        return evaluation.of_ignore_error(self)

    def __repr__(self):
        return "IgnoreError(%s)" % str(self.expression)


