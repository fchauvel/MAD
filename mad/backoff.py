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


from random import randint


class ConstantDelay:
    """
    Generate a constant delay
    """

    @staticmethod
    def factory():
        return ConstantDelay()

    def __init__(self, delay=10):
        self._delay = delay
        self._rejection_count = 0

    def new_rejection(self):
        self._rejection_count += 1

    def new_success(self):
        self._rejection_count = 0

    @property
    def delay(self):
        return self._delay * self._factor

    @property
    def _factor(self):
        return 1


class FibonacciDelay(ConstantDelay):
    """
    Delay computed according following the Fibonacci sequence
    """

    @staticmethod
    def factory():
        """
        :return: a new instance of exponential back off strategy
        """
        return FibonacciDelay()

    def __init__(self, delay=10):
        super().__init__(delay)

    @ConstantDelay._factor.getter
    def _factor(self):
        return self._fib(self._rejection_count)

    def _fib(self, n):
        if n == 0: return 0
        elif n == 1: return 1
        else: return self._fib(n-1) + self._fib(n-2)


class ExponentialBackOff(ConstantDelay):
    """
    Exponential backoff, extend the delay by a random factor between 0 and 2^r-1, where r is the number
    of rejections
    """

    @staticmethod
    def factory():
        """
        :return: a new instance of exponential back off strategy
        """
        return ExponentialBackOff()

    def __init__(self, base_delay=10):
        super().__init__(base_delay)

    @ConstantDelay._factor.getter
    def _factor(self):
        return randint(0, 2 ** self._rejection_count - 1)


