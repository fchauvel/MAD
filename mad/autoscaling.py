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


class Rule:

    def __init__(self, guard, action):
        self.guard = guard
        self.action = action

    def applies_to(self, utilisation):
        return self.guard(utilisation)

    def compute(self, count):
        return self.action(count)


class AutoScaling:

    def __init__(self, service, minimum, maximum, lower_bound, upper_bound):
        self._service = service
        self._minimum = minimum
        self._maximum = maximum
        self._rules = [
            Rule(lambda utilisation: utilisation < lower_bound,
                 lambda count: count - 1),
            Rule(lambda utilisation: utilisation > upper_bound,
                 lambda count: count + 1)
        ]

    def adjust(self):
        self._set(self._filter(self._update()))

    def _update(self):
        for any_rule in self._rules:
            if any_rule.applies_to(self._service.utilisation):
                return any_rule.compute(self._service.worker_count)
        return self._service.worker_count

    def _filter(self, worker_count):
        if self._minimum < worker_count < self._maximum:
            return worker_count
        return self._service.worker_count

    def _set(self, new_value):
        self._service.set_worker_count(new_value)
