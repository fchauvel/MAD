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
from io import StringIO

from mad.des2.repository import InMemoryDataSource, Project
from mad.des2.monitoring import CSVReportFactory, CSVReport


class ReportFactoryTests(TestCase):

    def test_report_unicity(self):
        factory = CSVReportFactory(Project("test.mad", 25), InMemoryDataSource())

        report1 = factory.report_for_service("my-service")
        report2 = factory.report_for_service("my-service")

        self.assertIsNotNone(report1)
        self.assertIsNotNone(report2)
        self.assertIs(report1, report2)


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
