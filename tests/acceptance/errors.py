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

from tests.acceptance.commons import MadAcceptanceTests


class ErrorsTests(MadAcceptanceTests):

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
