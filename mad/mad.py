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
from mad.experiments.sensitivity import SensitivityAnalysis, RejectionRate, ResponseTime, ClientRequestRate, SensitivityAnalysisListener
from mad.experiments.sandbox import Sandbox


class Mad:
    """
    Facade that provide access to all the experiments supported by MAD
    """

    def sensitivity_analysis(self, controller):
        analysis = SensitivityAnalysis(listener=controller)
        analysis.run_count = 100
        analysis.parameters = [ RejectionRate(), ResponseTime(), ClientRequestRate() ]
        analysis.run()

    def sandbox(self):
        sandbox = Sandbox()
        sandbox.run()


class UI:
    """
    The user interface, where MAD reports progress
    """

    def __init__(self, output = stdout):
        self._output = output

    def print_version(self):
        self.print("MAD v%s" % __version__)

    def print_copyright(self):
        self.print("Copyright (C) 2015 Franck Chauvel")

    def print_disclaimer(self):
        self.print("This program comes with ABSOLUTELY NO WARRANTY\n"
                   "This is free software, and you are welcome to redistribute it\n"
                   "under certain conditions.")

    def unknown_command(self, command, candidates):
        self.print("Error: Unknown command '%s'" % command)
        self.print("Commands are: ", ', '.join(candidates))

    def print(self, message):
        print(message, file=self._output)

    def show(self, message):
        print(message, file=self._output, end="\r")


class Controller(SensitivityAnalysisListener):
    """
    Synchronize the Facade with the UI
    """

    def __init__(self, engine=Mad(), ui=UI()):
        self._mad = engine
        self._ui = ui
        self._legal_commands = {
            "-sa": self._sensitivity_analysis,
            "--sensitivity-analysis": self._sensitivity_analysis,
            "-sb": self._sandbox,
            "--sandbox": self._sandbox
        }

    def _sensitivity_analysis(self):
        self._ui.print("---------------------")
        self._ui.print("Sensitivity Analysis:")
        self._mad.sensitivity_analysis(self)
        self._ui.print("")

    def sensitivity_of(self, parameter, value, run):
        self._ui.show(" - %s: %.2f (Run %3d)" % (parameter.name, value, run))

    def sensitivity_analysis_complete(self, parameter):
        self._ui.show(" - %s ... DONE                  " % parameter.name)

    def _sandbox(self):
        self._ui.print("------------")
        self._ui.print("Sandbox")
        self._mad.sandbox()

    def run(self, commands):
        self._ui.print_version()
        self._ui.print_copyright()
        self._ui.print_disclaimer()
        if len(commands) == 0:
            self._sensitivity_analysis()
        else:
            for each_command in commands:
                if self._is_defined(each_command):
                    self._execute(each_command)
                else:
                    self._ui.unknown_command(each_command, self._legal_command_names())

    def _is_defined(self, command):
        return command in self._legal_commands

    def _execute(self, command):
        self._legal_commands[command]()

    def _legal_command_names(self):
        return [ name for name in self._legal_commands ]



