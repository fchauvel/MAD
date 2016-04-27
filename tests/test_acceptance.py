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


class AcceptanceTests(TestCase):

    IDENTIFIER = "1"
    MODEL_NAME = "test"
    LOCATION = MODEL_NAME + ".mad"

    def setUp(self):
        Arguments._identifier = MagicMock(return_value=self.IDENTIFIER)
        self.display = StringIO()
        self.file_system = InMemoryFileSystem()

    def test_client_server(self):
        self.file_system.define("test.mad", ""
                                            "service DB {"
                                            "   operation Insert {"
                                            "      think 5"
                                            "      query Mirror/Insert"
                                            "      fail 0.5"
                                            "   }"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "service Mirror {"
                                            "   operation Insert {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "      retry (limit: 5, delay:exponential(5)) {"
                                            "           invoke DB/Insert"
                                            "      }"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_priority_scheme(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            ""
                                            "client Browser_A {"
                                            "   every 1 {"
                                            "      query DB/Select {priority: 10}"
                                            "   }"
                                            "}"
                                            ""
                                            "client Browser_B {"
                                            "   every 10 {"
                                            "      query DB/Select {priority: 0}"
                                            "   }"
                                            "}")

        self._execute([self.LOCATION, 22])

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_successful_invocations("Browser_A", 3)
        self._verify_successful_invocations("Browser_B", 0)
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_fail(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      fail"
                                            "   }"
                                            "}"
                                            ""
                                            "client Browser {"
                                            "   every 2 {"
                                            "       query DB/Select "
                                            "   }"
                                            "}")

        self._execute([self.LOCATION, 100])

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_successful_invocations("Browser", 0)
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_retry(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      fail"
                                            "   }"
                                            "}"
                                            ""
                                            "client Browser {"
                                            "   every 100 {"
                                            "       retry(delay:constant(2), limit:10) {"
                                            "           query DB/Select"
                                            "       }"
                                            "   }"
                                            "}")

        self._execute([self.LOCATION, 200])

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_successful_invocations("Browser", 0)
        self._verify_request_count("DB", 10)
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_ignore_error(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      fail"
                                            "   }"
                                            "}"
                                            ""
                                            "client Browser {"
                                            "   every 20 {"
                                            "       ignore {"
                                            "           query DB/Select"
                                            "       }"
                                            "   }"
                                            "}")

        self._execute([self.LOCATION, 40])

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_successful_invocations("Browser", 1)
        self._verify_reports_for(["DB"])
        self._verify_log()


    def test_timeouts(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 10"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 20 {"
                                            "      query DB/Select {timeout: 5}"
                                            "   }"
                                            "}")

        self._execute([self.LOCATION, 100])

        self._verify_opening()
        self._verify_valid_model()
        self._verify_no_warnings()
        self._verify_successful_invocations("Browser", 0)
        self._verify_reports_for(["DB"])
        self._verify_log()

    def test_invalid_simulation_length(self):
        self.file_system.define("test.mad", "whatever, as it will not be parsed!")

        wrong_length = "wrong length"
        invalid_command_line = ["test.mad", wrong_length]
        self._execute(invalid_command_line)

        self._verify_opening()
        self._verify_invalid_simulation_length(wrong_length)
        self._verify_usage()

    def test_invalid_simulation_file(self):
        self.file_system.define("test.mad", "whatever, as it will not be parsed!")

        wrong_file = 1
        invalid_command_line = [wrong_file, 1000]
        self._execute(invalid_command_line)

        self._verify_opening()
        self._verify_invalid_simulation_file(wrong_file)
        self._verify_usage()

    def test_invalid_parameter_count(self):
        self.file_system.define("test.mad", "whatever, as it will not be parsed!")

        invalid_command_line = ["test.mad", 1000, "an extra parameter"]
        self._execute(invalid_command_line)

        self._verify_opening()
        self._verify_invalid_parameter_count(len(invalid_command_line))
        self._verify_usage()

    def test_error_empty_service(self):
        self.file_system.define("test.mad", "service DB { \n"
                                            "   settings { \n"
                                            "       queue: LIFO \n"
                                            "   } \n"
                                            "} \n"
                                            "client Browser { \n"
                                            "   every 5 { \n"
                                            "      query DB/Insert \n"
                                            "   } \n"
                                            "} \n")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_syntax_error(line=5, hint="}")

    def test_error_unknown_operation(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Insert"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_unknown_operation("DB", "Insert")
        self._verify_operation_never_invoked("DB", "Select")

    def test_error_duplicate_service(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "service DB {"
                                            "   operation Insert {"
                                            "      think 17"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_duplicate_service("DB")

    def test_error_duplicate_client(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5 "
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "   }"
                                            "}"
                                            "client Browser { "
                                            "   every 10 {"
                                            "       invoke DB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_duplicate_client("Browser")

    def test_error_duplicate_entity_name(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "client DB {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_duplicate_entity_name("DB")

    def test_error_duplicate_operation(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "   operation Select  {"
                                            "      think 17"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_duplicate_operation("DB", "Select")

    def test_warning_operation_never_invoked(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "   operation Insert {"
                                            "      think 17"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_valid_model()
        self._verify_operation_never_invoked("DB", "Insert")

    def test_error_unknown_service(self):
        self.file_system.define("test.mad", "service DB {"
                                            "   operation Select {"
                                            "      think 5"
                                            "   }"
                                            "}"
                                            "client Browser {"
                                            "   every 5 {"
                                            "      query DBBBB/Select"
                                            "   }"
                                            "}")

        self._execute()

        self._verify_opening()
        self._verify_model_loaded()
        self._verify_invalid_model()
        self._verify_unknown_service("DBBBB")

    def _execute(self, command_line = None):
        if not command_line:
            command_line = [self.LOCATION, 1000]
        mad = Controller(self.display, self.file_system)
        self.simulation = mad.execute(*command_line)

    def _verify_successful_invocations(self, entity_name, expected_count):
        entity = self.simulation.environment.look_up(entity_name)
        self.assertEqual(expected_count, entity.monitor.success_count)

    def _verify_request_count(self, entity_name, expected_count):
        entity = self.simulation.environment.look_up(entity_name)
        monitor = entity.look_up(Symbols.MONITOR)
        self.assertEqual(expected_count, monitor.statistics.total_request_count)

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
