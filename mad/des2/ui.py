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


class Display:

    def simulation_started(self):
        pass

    def update(self, time):
        pass

    def simulation_complete(self):
        pass


class CommandLineInterface:

    def __init__(self, display, repository):
        self.display = display
        self.repository = repository

    def simulate(self, model, limit):
        simulation = self.repository.load(model)
        simulation.run_until(limit, self.display)
