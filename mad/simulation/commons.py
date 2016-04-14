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


class SimulatedEntity:
    """
    Factor out commonalities between all simulated entities
    """

    def __init__(self, name, environment):
        self.environment = environment
        self.name = name
        self.simulation = self.environment.look_up(Symbols.SIMULATION)

    @property
    def schedule(self):
        return self.simulation.schedule

    def log(self, message, values):
        now = self.schedule.time_now
        caller = self.look_up(Symbols.SELF)
        self.simulation.log.record(now, caller.name, message % values)

    def look_up(self, symbol):
        return self.environment.look_up(symbol)

    @property
    def factory(self):
        return self.simulation.factory

    def create_report(self, format):
        return self.simulation._storage.report_for(self.name, format)

    def next_request_id(self):
        return self.simulation.next_request_id()

