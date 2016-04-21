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

from unittest import TestCase
from mock import MagicMock
from tests.fakes import InMemoryFileSystem

from io import StringIO

from mad.monitoring import CSVReport
from mad.ui import Controller, Arguments


class MonitoringTests(TestCase):

    MAD_FILE = "test.mad"

    def setUp(self):
        self.file_system = InMemoryFileSystem()

    def test_loading(self):
        Arguments._identifier = lambda s: "1"

        self.file_system.define(
            self.MAD_FILE,
            "service DB {"
            "  operation Select {"
            "      think 5"
            "   }"
            "}"
            "client Browser {"
            "  every 10 {"
            "      query DB/Select"
            "   }"
            "}")

        controller = Controller(StringIO(), self.file_system)

        controller.execute("test.mad", "25")

        data = self.file_system.opened_files["test_1/DB.log"].getvalue().split("\n")
        self.assertEqual(4, len(data), data) # header line, + Monitoring at 10, 20 + newline


class ReportTests(TestCase):

    def test_report(self):
        output = StringIO()
        report = CSVReport(output,
                           [    ("time", "%3d"),
                                ("queue_length", "%3d")])

        report(time=5, queue_length=3)
        report(time=10, queue_length=6)

        expected_csv = "time, queue length\n" \
                       "  5,   3\n" \
                       " 10,   6\n"

        self.assertEqual(expected_csv, output.getvalue())
