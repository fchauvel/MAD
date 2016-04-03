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

    def __init__(self, environment, period, strategy):
        super().__init__(self.NAME, environment)
        self.period = period
        self.schedule.every(period, self.auto_scale)
        self.strategy = strategy

    def auto_scale(self):
        service = self.look_up(Symbols.SERVICE)
        self.strategy.adjust(service)


class Rule:

    def __init__(self, guard, action):
        self.guard = guard
        self.action = action

    def applies_to(self, utilisation):
        return self.guard(utilisation)

    def compute(self, count):
        return self.action(count)


class AutoScalingStrategy:

    def __init__(self, minimum, maximum, lower_bound, upper_bound):
        self._minimum = minimum
        self._maximum = maximum
        self._rules = [
            Rule(lambda utilisation: utilisation < lower_bound,
                 lambda count: count - 1),
            Rule(lambda utilisation: utilisation > upper_bound,
                 lambda count: count + 1)
        ]

    def adjust(self, service):
        assert service, "Invalid service (found '%s')" % service
        utilisation = service.utilisation
        worker_count = service.worker_count

        def update():
            for any_rule in self._rules:
                if any_rule.applies_to(utilisation):
                    return any_rule.compute(worker_count)
            return worker_count

        def filter(worker_count):
            if self._minimum <= worker_count <= self._maximum:
                return worker_count
            return service.worker_count

        def set(new_value):
            service.set_worker_count(new_value)

        set(filter(update()))
