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

from random import gauss


class Function:
    """
    The signature of a function, parameterised by time
    """

    def value_at(self, time):
        pass


class Constant(Function):
    """
    A constant value over time
    """

    def __init__(self, value):
        self._value = value

    def value_at(self, time):
        return self._value


class FunctionDecorator(Function):
    """
    Decorate a given function
    """

    def __init__(self, delegate):
        self._delegate = delegate

    @property
    def delegate(self):
        return self._delegate


class GaussianNoise(FunctionDecorator):

    def __init__(self, delegate, variance=1):
        super().__init__(delegate)
        self._variance = variance

    def value_at(self, time):
        return self.delegate.value_at(time) + self._noise()

    def _noise(self):
        return gauss(0, self._variance)


class Bound(FunctionDecorator):
    """
    Check the output of the given function with respect to the given bound
    """

    def __init__(self, delegate, bound):
        super().__init__(delegate)
        self._bound = bound

    @property
    def bound(self):
        return self._bound

    def exceeds_bound(self, value):
        pass

    def value_at(self, time):
        result = self.delegate.value_at(time)
        if self.exceeds_bound(result):
            return self._bound
        else:
            return result


class LowerBound(Bound):
    """
    Check that the given function outputs a value above the bound
    """

    def __init__(self, delegate, lower_bound):
        super().__init__(delegate, lower_bound)

    def exceeds_bound(self, value):
        return value < self.bound


class UpperBound(Bound):
    """
    Check that the given function outputs a value below the bound
    """

    def __init__(self, delegate, upper_bound):
        super().__init__(delegate, upper_bound)

    def exceeds_bound(self, value):
        return value > self.bound
