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

from mad.evaluation import Symbols
from mad.simulation.commons import SimulatedEntity


class AutoScaler(SimulatedEntity):
    """
    The 'AutoScaler' periodically recomputes the number of worker for the service in its logical scope.
    """
    NAME = "!Autoscaler"
    UPPER = 1
    LOWER = 0

    def __init__(self, environment, period, limits, strategy):
        super().__init__(self.NAME, environment)
        self.period = period
        self.schedule.every(period, self.auto_scale)
        self.limits = limits
        self.strategy = strategy

    def auto_scale(self):
        service = self.look_up(Symbols.SERVICE)
        new_worker_count = self._filter(self.strategy.adjust(service))
        service.set_worker_count(new_worker_count)

    def _filter(self, value):
        if self._too_low(value):
            return self._minimum()
        elif self._too_high(value):
            return self._maximum()
        else:
            return value

    def _too_high(self, value):
        return value > self._maximum()

    def _too_low(self, value):
        return value < self._minimum()

    def _maximum(self):
        return self.limits[self.UPPER]

    def _minimum(self):
        return self.limits[self.LOWER]


class Rule:
    """
    AutoScaling rule such as 'when x < 20, then worker += 1'
    """

    def __init__(self, guard, action):
        self.guard = guard
        self.action = action

    def applies_to(self, utilisation):
        return self.guard(utilisation)

    def compute(self, count):
        return self.action(count)


class RuleBasedStrategy:

    def __init__(self, lower_threshold, upper_threshold):
        self._rules = [
            Rule(lambda utilisation: utilisation < lower_threshold,
                 lambda count: count - 1),
            Rule(lambda utilisation: utilisation > upper_threshold,
                 lambda count: count + 1),
            # Default case: the identity rule that always triggers
            Rule(lambda utilisation: True,
                 lambda count: count)
        ]

    def adjust(self, service):
        assert service, "Invalid service (found '%s')" % service
        for any_rule in self._rules:
            if any_rule.applies_to(service.utilisation):
                return any_rule.compute(service.worker_count)
