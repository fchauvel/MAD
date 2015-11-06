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



class BackOffStrategy:
    """
    The interface of all back off strategies
    """

    def __init__(self, delay):
        self._delay = delay

    @property
    def delay(self):
        return self._delay


class ExponentialBackOff(BackOffStrategy):
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
        self._rejection_count = 0

    def new_rejection(self):
        self._rejection_count += 1

    def new_success(self):
        self._rejection_count = 0

    @BackOffStrategy.delay.getter
    def delay(self):
        return super().delay * self._factor()

    def _factor(self):
        return randint(0, 2 ** self._rejection_count - 1)


