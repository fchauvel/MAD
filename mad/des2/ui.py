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

from mad import __version__ as MAD_VERSION


class Display:

    def __init__(self, output):
        self.output = output

    def boot_up(self):
        self.output.write("MAD %s \n" % MAD_VERSION)
        self.output.write("Copyright (c) 2015 - 2016 Franck CHAUVEL\n")
        self.output.write("\n")
        self.output.write("This program comes with ABSOLUTELY NO WARRANTY.\n"
                          "This is free software, and you are welcome to redistribute it\n"
                          "under certain conditions.\n")
        self.output.write("\n")

    def simulation_started(self, file):
        self.output.write("Loading '%s'\n" % file)

    def update(self, current_time, end):
        progress = current_time / end * 100
        self.output.write("\rSimulation %d %%" % progress)

    def simulation_complete(self):
        self.output.write("\nSimulation complete.\n")


class CommandLineInterface:

    def __init__(self, display, repository):
        self.display = display
        self.repository = repository

    def simulate(self, model, limit):
        self.display.boot_up()
        self.display.simulation_started(model)
        simulation = self.repository.load(model)
        simulation.run_until(limit, self.display)
        self.display.simulation_complete()

    def simulate_arguments(self, arguments):
        if len(arguments) != 2:
            raise ValueError("Missing arguments (expected [my-file.mad] [simulation-length], but found '%s')" % arguments)
        file_name = self._extract_file_name(arguments)
        length = self._extract_length(arguments)
        self.simulate(file_name, length)

    def _extract_file_name(self, arguments):
        result = arguments[0]
        if not isinstance(result, str):
            raise ValueError("Expecting 'MAD file' as Argument 1, but found '%s'" % arguments[0])
        return result

    def _extract_length(self, arguments):
        try:
            return int(arguments[1])
        except ValueError:
            raise ValueError("Expecting simulation length as Argument 2, but found '%s'" % arguments[1])
