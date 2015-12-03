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
from mad.experiments.sensitivity import SensitivityAnalysisController
from mad.experiments.sandbox import Sandbox as SandboxExp



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


class Controller:

    def __init__(self, ui):
        self._ui = ui

    def print_version(self):
        self._ui.print("MAD v%s" % __version__)

    def print_copyright(self):
        self._ui.print("Copyright (C) 2015 Franck Chauvel")

    def print_disclaimer(self):
        self._ui.print("This program comes with ABSOLUTELY NO WARRANTY\n"
                       "This is free software, and you are welcome to redistribute it\n"
                        "under certain conditions.")

    def sandbox(self):
        self._ui.print("------------")
        self._ui.print("Sandbox")
        sandbox = SandboxExp()
        sandbox.run()

    def sensitivity_analysis(self):
        self._ui.print("------------")
        self._ui.print("Sensitivity Analysis")
        analysis = SensitivityAnalysisController(self._ui)
        analysis.execute()

    def unknown_command(self, command):
        if command is None:
            self._ui.print("Error: no option given")
        else:
            self._ui.print("Unknown option '%s'" % command)


class Command:

    def send_to(self, controller):
        pass


class Macro(Command):

    def __init__(self, *steps):
        self._steps = steps

    def send_to(self, controller):
        for each_step in self._steps:
            each_step.send_to(controller)


class SensitivityAnalysis(Command):

    def send_to(self, controller):
        controller.sensitivity_analysis()


class Sandbox(Command):

    def send_to(self, controller):
        controller.sandbox()


class UnknownCommand(Command):

    def __init__(self, option):
        self._option = option

    def send_to(self, controller):
        controller.unknown_command(self._option)


class CommandFactory:

    LEGAL_COMMANDS = {
        "-sb": Sandbox,
        "--sandbox": Sandbox,
        "-sa": SensitivityAnalysis,
        "--sensitivity": SensitivityAnalysis
    }

    @staticmethod
    def parse_all(command_line):
        commands = [ CommandFactory.parse(each_option) for each_option in command_line ]
        return Macro(*commands)

    @staticmethod
    def parse(option):
        if option in CommandFactory.LEGAL_COMMANDS:
            return CommandFactory.LEGAL_COMMANDS[option]()
        else:
            return UnknownCommand(option)
