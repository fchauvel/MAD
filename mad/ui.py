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

from re import search
from datetime import datetime

from mad.storage import DataStorage
from mad.validation.engine import Validator, InvalidModel

from mad.parsing import Parser

from mad.simulation.factory import Simulation

from mad.log import FileLog
from mad.monitoring import CSVReport


class Messages:

    VERSION = "MAD v{version:s}\n"

    COPYRIGHT = "Copyright (c) {years:s} {owner:s}\n"

    DISCLAIMER = "This program comes with ABSOLUTELY NO WARRANTY.\n" \
                 "This is free software, and you are welcome to redistribute it\n" \
                 "under certain conditions.\n"

    MODEL_LOADED = "MAD model loaded from '{location:s}'\n"

    SIMULATION_PROGRESS = "\rSimulation {progress:.2f} %"

    RESULTS_AVAILABLE = "\n\nSee results in directory: ./{location:s}/\n"

    INVALID_MODEL = "Error, the model is invalid\n"

    ERROR = " - {severity:8s} "

    ERROR_UNKNOWN_OPERATION = ERROR + "Unknown operation '{service}::{operation}'\n"

    ERROR_NEVER_INVOKED_OPERATION = ERROR + "Operation '{service}::{operation}' is never invoked.\n"

    ERROR_DUPLICATE_SERVICE = ERROR + "Service '{service}' is defined multiple times.\n"

    ERROR_DUPLICATE_OPERATION = ERROR + "Operation '{service}::{operation}' is defined multiple times.\n"

    ERROR_UNKNOWN_SERVICE = ERROR + "Unknown service '{service}'\n"

    SEVERITY_ERROR = "error"

    SEVERITY_WARNING = "warning"


class Controller:

    def __init__(self, output, file_system):
        self.display = Display(output)
        self.file_system = file_system
        self.storage = None

    def execute(self, *command_line):
        try:
            self.display.boot_up()
            arguments = self._parse(command_line)
            expression = self._load(arguments)
            self._validate(expression)
            return self._simulate(expression, arguments)

        except InvalidModel as error:
            self._report_invalid_model(error)

    def _report_invalid_model(self, error):
        self.display.invalid_model()
        for each_issue in error.issues:
            each_issue.accept(self.display)

    def _parse(self, command_line):
        return Arguments(command_line)

    def _load(self, arguments):
        self.storage = DataStorage(
            Parser(self.file_system, arguments._file_name),
            FileLog(self.file_system.open_output_stream(arguments.log_file), Arguments.LOG_FORMAT),
            lambda name, format: CSVReport(self.file_system.open_output_stream(arguments.report_for(name)), format))
        self.display.model_loaded(arguments)
        expression = self.storage.model()
        return expression

    def _validate(self, expression):
        validator = Validator()
        validator.validate(expression)
        if validator.raised_warnings():
            for each_warning in validator.errors:
                each_warning.accept(self.display)

    def _simulate(self, expression, arguments):
        simulation = Simulation(self.storage)
        simulation.evaluate(expression)
        simulation.run_until(arguments._time_limit, self.display)
        self.display.simulation_complete(arguments)
        return simulation


class Display:
    """
    Abstract the display where that report and format the progress of the simulation
    """

    def __init__(self, output):
        self.output = output

    def _new_line(self):
        self.output.write("\n")

    def _format(self, message, **kwargs):
        self.output.write(message.format(**kwargs))

    def boot_up(self):
        self._show_version()
        self._show_copyright()
        self._new_line()
        self._format(Messages.DISCLAIMER)
        self._new_line()

    def _show_copyright(self):
        from mad import __copyright_years__ as YEARS
        from mad import __copyright_owner__ as OWNER
        self._format(Messages.COPYRIGHT, years=YEARS, owner=OWNER)

    def _show_version(self):
        from mad import __version__ as MAD_VERSION
        self._format(Messages.VERSION, version=MAD_VERSION)

    def model_loaded(self, project):
        self._format(Messages.MODEL_LOADED, location=project._file_name)

    def update(self, current_time, end):
        progress = current_time / end * 100
        self._format(Messages.SIMULATION_PROGRESS, progress=progress)

    def simulation_complete(self, project):
        self._format(Messages.RESULTS_AVAILABLE, location=project._output_directory)

    def invalid_model(self):
        self._format(Messages.INVALID_MODEL)

    def unknown_service(self, error):
        self._format(
            Messages.ERROR_UNKNOWN_SERVICE,
            severity=self._severity_of(error),
            service=error.service)

    def unknown_operation(self, error):
        self._format(
            Messages.ERROR_UNKNOWN_OPERATION,
            severity=self._severity_of(error),
            service=error.service,
            operation=error.operation)

    def never_invoked_operation(self, error):
        self._format(
            Messages.ERROR_NEVER_INVOKED_OPERATION,
            severity=self._severity_of(error),
            service=error.service,
            operation=error.operation)

    def duplicate_service(self, error):
        self._format(Messages.ERROR_DUPLICATE_SERVICE,
                     severity=self._severity_of(error),
                     service=error.service)

    def duplicate_operation(self, error):
        self._format(Messages.ERROR_DUPLICATE_OPERATION,
                     severity=self._severity_of(error),
                     operation=error.operation,
                     service=error.service)

    def _severity_of(self, error):
        return Messages.SEVERITY_ERROR if error.is_error() else Messages.SEVERITY_WARNING


class Arguments:
    """
    Convert the arguments given on the command line into a MadProject
    """

    BASE_NAME = r"([^\\/]+)\.(\w+)$"
    LOG_FILE = "trace.log"
    LOG_FORMAT = "%5d %-20s %-s\n"
    PATH_TO_LOG_FILE = "{directory:s}/{log_file:s}"
    OUTPUT_DIRECTORY = "{name:s}_{identifier:s}"
    REPORT = "{directory:s}/{entity:s}.log"

    def __init__(self, arguments):
        self._arguments = arguments
        self._file_name = self._extract_file_name()
        self._time_limit = self._extract_length()

    def _extract_file_name(self):
        result = self._arguments[0]
        if not isinstance(result, str):
            raise ValueError("Expecting 'MAD file' as Argument 1, but found '%s'" % self._arguments[0])
        return result

    def _extract_length(self):
        try:
            return int(self._arguments[1])
        except ValueError:
            raise ValueError("Expecting simulation length as Argument 2, but found '%s'" % self._arguments[1])

    @property
    def log_file(self):
        return self.PATH_TO_LOG_FILE.format(
            directory=self._output_directory,
            log_file=self.LOG_FILE)

    @property
    def _output_directory(self):
        return self.OUTPUT_DIRECTORY.format(
            name=self._model_name,
            identifier=self._identifier())

    @property
    def _model_name(self):
        return search(self.BASE_NAME, self._file_name).group(1)

    @staticmethod
    def _identifier():
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def report_for(self, entity):
        return self.REPORT.format(
            directory=self._output_directory,
            entity=entity
        )
