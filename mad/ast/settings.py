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


class NoThrottlingSettings(Expression):
    """
    Configuration of a "no throttling" policy
    """

    def __init__(self):
        super().__init__()

    def accept(self, evaluation):
        return evaluation.of_no_throttling(self)


class TailDropSettings(Expression):
    """
    Configuration of a "tail drop" throttling policy
    """

    def __init__(self, capacity):
        super().__init__()
        self.capacity = capacity

    def accept(self, evaluation):
        return evaluation.of_tail_drop(self)


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

    def __init__(self, period=30, limits=(1, 1)):
        super().__init__()
        if not isinstance(period, int):
            raise ValueError("Expecting integer value for period, but found '%1$s' (%2$s)" % (str(period), type(period)))
        self.period = period

        if not isinstance(limits, tuple):
            raise ValueError("Expecting interval (min, max) for limits but found '%1$s'" % str(limits))
        self.limits = limits

    def accept(self, evaluation):
        return evaluation.of_autoscaling(self)

    def __repr__(self):
        return "Autoscaling(%1$d, %2$s)" % (self.period, str(self.limits))


class Settings(Expression):

    def __init__(self, queue=None, autoscaling=None, throttling=None):
        super().__init__()
        self.queue = queue or FIFO()
        self.autoscaling = autoscaling or Autoscaling()
        self.throttling = throttling or NoThrottlingSettings()

    def accept(self, evaluation):
        return evaluation.of_settings(self)

    def __repr__(self):
        return "Settings(queue: %s)" % str(self._queue)