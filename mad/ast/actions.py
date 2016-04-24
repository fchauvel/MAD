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
    DEFAULT_PRIORITY = 5

    def __init__(self, service, operation, priority):
        super().__init__()
        self.service = service
        self.operation = operation
        self.priority = priority

    def accept(self, evaluation):
        raise NotImplementedError("Invocation::accept(evaluation) is abstract!")


class Trigger(Invocation):
    """
    An non-blocking invocation of a remote operation
    """

    def __init__(self, service, operation, priority=None):
        super().__init__(service, operation, priority or self.DEFAULT_PRIORITY)

    def accept(self, evaluation):
        return evaluation.of_trigger(self)

    def __repr__(self):
        return "Trigger(%s, %s, %d)" % (self.service, self.operation, self.priority)


class Query(Invocation):
    """
    A blocking invocation of a remote operation
    """

    def __init__(self, service, operation, priority=None, timeout=None):
        super().__init__(service, operation, priority or self.DEFAULT_PRIORITY)
        self.timeout = timeout

    def accept(self, evaluation):
        return evaluation.of_query(self)

    @property
    def has_timeout(self):
        return self.timeout is not None

    def __repr__(self):
        return "Query(%s, %s, %d)" % (self.service, self.operation, self.priority)


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


class Fail(Action):
    """
    Fail with a given probability
    """
    NEGATIVE_PROBABILITY = "Negative probability (found {0:5.2f})"

    def __init__(self, probability=1.0):
        super().__init__()
        assert probability >= 0., self.NEGATIVE_PROBABILITY.format(probability)
        self.probability = probability

    def accept(self, evaluation):
        return evaluation.of_fail(self)

    def __repr__(self):
        return "Fail(%d)" % self.probability


class Delay(Expression):

    CONSTANT = "constant"
    EXPONENTIAL = "exponential"

    def __init__(self, base_delay=10, strategy= None):
        super().__init__()
        self.base_delay = base_delay
        self.strategy = strategy or self.CONSTANT


class Retry(Expression):
    """
    Retry an action a given number of time
    """
    DEFAULT_DELAY = Delay()

    def __init__(self, expression, limit=None, delay=None):
        super().__init__()
        self.expression = expression
        assert not limit or limit > 0, "Retry limit must be strictly positive (found %d)" % limit
        self.limit = limit
        self.delay = delay or self.DEFAULT_DELAY

    def accept(self, evaluation):
        return evaluation.of_retry(self)

    def __repr__(self):
        return "Retry(%s, %d)" % (str(self.expression), self.limit)


class IgnoreError(Expression):
    """
    Ignore error occuring during the evaluation of the given expression
    """

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def accept(self, evaluation):
        return evaluation.of_ignore_error(self)

    def __repr__(self):
        return "IgnoreError(%s)" % str(self.expression)
