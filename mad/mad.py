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


from sys import stdout

from mad import __version__


class UI:
    """
    The user interface, where MAD reports progress
    """

    def __init__(self, output = stdout):
        self._output = output

    def unknown_command(self, command, candidates):
        self.print("Error: Unknown command '%s'" % command)
        self.print("Commands are: ", ', '.join(candidates))

    def print(self, message):
        print(message, file=self._output)

    def show(self, message):
        print(message, file=self._output, end="\r")


class Builder:

    def assemble(self, system, environment):
        pass


class Repository:

    def __init__(self, parser):
        self._parser = parser

    def load(self, path_to_file):
        with open(path_to_file) as source_file:
            text = source_file.readlines()
            return self._parser.parse(text)


class Controller:

    ARCHITECTURE = 0
    ENVIRONMENT = 1

    def __init__(self, ui, repository, builder):
        self._ui = ui
        self._repository = repository
        self._builder = builder

    def simulate(self, arguments):
        self._print_header()

        self._ui.show("Loading architecture from '%s' ... " % arguments[self.ARCHITECTURE])
        system = self._repository.load(arguments[self.ARCHITECTURE])

        self._ui.print("Loading environment from '%s' ... " % arguments[self.ENVIRONMENT])
        environment = self._repository.load(arguments[self.ENVIRONMENT])

        self._ui.print("Starting simulation")
        simulation = self._builder.assemble(system, environment)
        simulation.run_until(1000, 30)

    def _print_header(self):
        self._print_version()
        self._print_copyright()
        self._print_disclaimer()
        self._ui.print("")

    def _print_version(self):
        self._ui.print("MAD v%s" % __version__)

    def _print_copyright(self):
        self._ui.print("Copyright (C) 2015 Franck Chauvel")

    def _print_disclaimer(self):
        self._ui.print("This program comes with ABSOLUTELY NO WARRANTY\n"
                       "This is free software, and you are welcome to redistribute it\n"
                       "under certain conditions.")