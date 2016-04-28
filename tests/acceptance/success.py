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


class SuccessfulTests(MadAcceptanceTests):

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
        self._verify_model_copy()

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
        self._verify_model_copy()

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
        self._verify_model_copy()

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
        self._verify_model_copy()

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
        self._verify_model_copy()


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
        self._verify_model_copy()
