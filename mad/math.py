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
from collections import namedtuple


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


Point = namedtuple("Point", ["time", "value"])


class Interpolation(Function):

    def __init__(self, default, points):
        self._default = default
        self._points = sorted(points, key=lambda p: p.time)

    def value_at(self, time):
        if len(self._points) == 0:
            return self._default
        if self._points[0].time > time or time > self._points[-1].time:
            return self._default
        else:
            (lower, upper) = self._find_bounds(time)
            return self._interpolate_between(time, lower, upper)

    def _find_bounds(self, time):
        for (index, point) in enumerate(self._points):
            if point.time >= time:
                return (self._points[index-1], point)
        raise ValueError("Could not find bounds for time=%d in points '%s'" % (time, str(self._points)))

    @staticmethod
    def _interpolate_between(time, lower, upper):
        return lower.value + (upper.value - lower.value) * ((time - lower.time) / (upper.time - lower.time) )



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
