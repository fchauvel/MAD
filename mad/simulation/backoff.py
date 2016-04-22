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


class BackoffStrategy:

    def delay(self, attempt):
        raise NotImplementedError("BackoffStrategy::delay is abstract!")


class ConstantBackoff(BackoffStrategy):

    def __init__(self, base_delay):
        self.base_delay = base_delay

    def delay(self, attempts):
        return self.base_delay


class ExponentialBackoff(ConstantBackoff):

    def __init__(self, base_delay):
        super().__init__(base_delay)

    def delay(self, attempts):
        if attempts == 0:
            return 0
        else:
            limit = 2 ** attempts - 1
            return self._pick_up_to(limit) * self.base_delay

    @staticmethod
    def _pick_up_to(limit):
        return randint(0, limit)