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

from io import StringIO

from mad.ui import Arguments, Messages, Controller
from mad.evaluation import Symbols

from unittest import TestCase, skip
from mock import MagicMock

from tests.fakes import InMemoryFileSystem


class MadAcceptanceTests(TestCase):

    IDENTIFIER = "1"
    MODEL_NAME = "test"
    LOCATION = MODEL_NAME + ".mad"

    def setUp(self):
        Arguments._identifier = MagicMock(return_value=self.IDENTIFIER)
        self.display = StringIO()
        self.file_system = InMemoryFileSystem()

    def _execute(self, command_line = None):
        if not command_line:
            command_line = [self.LOCATION, 1000]
        mad = Controller(self.display, self.file_system)
        self.simulation = mad.execute(*command_line)

    def _verify_successful_task_count(self, entity_name, expected_count):
        entity = self.simulation.environment.look_up(entity_name)
        monitor = entity.look_up(Symbols.MONITOR)
        #self.assertEqual(expected_count, entity.monitor.success_count)
        self.assertEqual(expected_count, monitor.tasks.successful)

    def _verify_complete_task_count(self, entity_name, expected_count):
        entity = self.simulation.environment.look_up(entity_name)
        monitor = entity.look_up(Symbols.MONITOR)
        #self.assertEqual(expected_count, monitor.statistics.total_request_count)
        self.assertEqual(expected_count, monitor.tasks.complete)

    def _verify_opening(self):
        self._verify_version()
        self._verify_copyright()
        self._verify_disclaimer()

    def _verify_invalid_parameter_count(self, count):
        self._verify_output(Messages.INVALID_PARAMETER_COUNT, count=count)

    def _verify_invalid_simulation_length(self, wrong_length):
        self._verify_output(Messages.INVALID_SIMULATION_LENGTH, length=wrong_length)

    def _verify_invalid_simulation_file(self, wrong_file):
        self._verify_output(Messages.INVALID_SIMULATION_FILE, file=str(wrong_file))

    def _verify_usage(self):
        self._verify_output(Messages.USAGE)

    def _verify_model_loaded(self):
        self._verify_output(Messages.MODEL_LOADED, location=self.LOCATION)

    def _verify_disclaimer(self):
        self._verify_output(Messages.DISCLAIMER)

    def _verify_version(self):
        from mad import __version__ as MAD_VERSION
        self._verify_output(Messages.VERSION, version=MAD_VERSION)

    def _verify_copyright(self):
        from mad import __copyright_years__ as YEARS
        from mad import __copyright_owner__ as OWNER
        self._verify_output(Messages.COPYRIGHT, years=YEARS, owner=OWNER)

    def _verify_valid_model(self):
        self._verify_output_excludes(Messages.INVALID_MODEL)
        self._verify_output_excludes(Messages.SEVERITY_ERROR)

    def _verify_no_warnings(self):
        self._verify_output_excludes(Messages.SEVERITY_WARNING)

    def _verify_syntax_error(self, line, hint):
        self._verify_output(Messages.INVALID_SYNTAX, line=line, hint=hint)

    def _verify_invalid_model(self):
        self._verify_output(Messages.INVALID_MODEL)

    def _verify_unknown_operation(self, service_name, operation_name):
        self._verify_output(Messages.ERROR_UNKNOWN_OPERATION,
                            severity=Messages.SEVERITY_ERROR,
                            service=service_name,
                            operation=operation_name)

    def _verify_duplicate_service(self, service_name):
        self._verify_output(Messages.ERROR_DUPLICATE_IDENTIFIER,
                            severity=Messages.SEVERITY_ERROR,
                            identifier=service_name)

    def _verify_duplicate_client(self, client_name):
        self._verify_output(Messages.ERROR_DUPLICATE_IDENTIFIER,
                            severity=Messages.SEVERITY_ERROR,
                            identifier=client_name)

    def _verify_duplicate_entity_name(self, name):
        self._verify_output(Messages.ERROR_DUPLICATE_IDENTIFIER,
                            severity=Messages.SEVERITY_ERROR,
                            identifier=name)

    def _verify_duplicate_operation(self, service_name, operation_name):
        self._verify_output(Messages.ERROR_DUPLICATE_OPERATION,
                            severity=Messages.SEVERITY_ERROR,
                            operation=operation_name,
                            service=service_name)

    def _verify_operation_never_invoked(self, service_name, operation_name):
        self._verify_output(Messages.ERROR_NEVER_INVOKED_OPERATION,
                            severity=Messages.SEVERITY_WARNING,
                            operation=operation_name,
                            service=service_name)

    def _verify_unknown_service(self, service_name):
        self._verify_output(Messages.ERROR_UNKNOWN_SERVICE,
                            severity=Messages.SEVERITY_ERROR,
                            service=service_name)

    def _verify_output(self, message, **values):
        from re import search, escape
        text = escape(message.format(**values))
        output = self.display.getvalue()
        match = search(text, output)
        self.assertIsNotNone(match, "\nCould not found text '%s' in output:\n%s" % (str(text), output))

    def _verify_output_excludes(self, message, **values):
        from re import search, escape
        text = escape(message.format(**values))
        output = self.display.getvalue()
        match = search(text, output)
        self.assertIsNone(match, "\nFound unexpected text '%s' in output:\n%s" % (str(text), output))

    def _verify_reports_for(self, entities):
        for each_entity in entities:
            self._verify_report(each_entity)

    def _verify_report(self, entity):
        directory = Arguments.OUTPUT_DIRECTORY.format(name=self.MODEL_NAME, identifier=self.IDENTIFIER)
        report = Arguments.REPORT.format(entity=entity, directory=directory)
        self.assertTrue(self.file_system.has_file(report),
                        "Missing report for '%s' (file '%s').\n Existing files are %s" % (entity, report, str(self.file_system.opened_files.keys())))

    def _verify_log(self):
        directory = Arguments.OUTPUT_DIRECTORY.format(name=self.MODEL_NAME, identifier=self.IDENTIFIER)
        report = Arguments.PATH_TO_LOG_FILE.format(directory=directory, log_file=Arguments.LOG_FILE)
        self.assertTrue(self.file_system.has_file(report),
                        "Missing log file '%s'.\n Existing files are %s" % (report, str(self.file_system.opened_files.keys())))

    def _verify_model_copy(self):
        directory = Arguments.OUTPUT_DIRECTORY.format(name=self.MODEL_NAME, identifier=self.IDENTIFIER)
        model_copy = Arguments.PATH_TO_MODEL_COPY.format(directory=directory, file=self.MODEL_NAME+".mad")
        self.assertTrue(self.file_system.has_file(model_copy),
                        "Missing copy of the model '%s'.\n Existing files are %s" % (model_copy, str(self.file_system.opened_files.keys())))
