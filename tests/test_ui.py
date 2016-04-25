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
from re import search, escape, IGNORECASE
from unittest import TestCase

from mock import MagicMock, patch

from mad import __version__ as MAD_VERSION
from mad.ui import Display, Arguments, InvalidSimulationLength, InvalidSimulationModel, WrongNumberOfArguments


class DisplayTest(TestCase):

    def setUp(self):
        self.project = Arguments(["test.mad", "25"])
        self.output = StringIO()
        self.display = Display(self.output)

    def test_boot_up(self):
        self.display.boot_up()
        self._verify_output(MAD_VERSION)

    def test_simulation_started(self):
        self.display.model_loaded(self.project)
        self._verify_output(self.project._file_name)

    def test_simulation_update(self):
        self.display.update(20, 100)
        self._verify_output("20.00 %")

    def test_simulation_complete(self):
        self.display.simulation_complete(self.project)
        self._verify_output(self.project._output_directory)

    def _verify_output(self, expected_pattern):
        output = self.output.getvalue()
        match = search(escape(expected_pattern), output, IGNORECASE)
        self.assertIsNotNone(match, msg="Could not find '%s' in output '%s'" % (expected_pattern, output))

    def _make_fake_simulation(self):
        simulation = MagicMock()
        simulation.run_until = MagicMock()

        def run_simulation(limit, display):
            for i in range(1,6):
                display.update(i*5, limit)

        simulation.run_until.side_effect = run_simulation
        return simulation


class ArgumentsTest(TestCase):

    def test_parsing_parameter(self):
        project = Arguments(["test.mad", "25"])
        self.assertEqual("test.mad", project._file_name)
        self.assertEqual(25, project._time_limit)

    def test_detecting_missing_arguments(self):
        with self.assertRaises(WrongNumberOfArguments):
            Arguments([25])

    def test_detecting_wrong_arguments(self):
        with self.assertRaises(InvalidSimulationModel):
            Arguments([25, "test.mad"])

        with self.assertRaises(InvalidSimulationLength):
            Arguments(["test.mad", "25x"])

    def test_output_directory_is_in_the_current_directory(self):
        Arguments._identifier = MagicMock(return_value="1")

        tests = [
            ("foo/test.mad", "test_1"),
            ("foo/bar/test.mad", "test_1"),
            ("foo/bar\\test.mad", "test_1"),
            ("foo/bar\\test my file.mad", "test my file_1"),
            ("C:\\Users\\foo\\test.mad", "test_1"),
            ("/home/foo/test.mad", "test_1"),
            ("../test.mad", "test_1"),
            ("http://www.example.com/test.mad", "test_1")
        ]
        for (each_path, each_expected_output) in tests:
            arguments = Arguments([each_path, "25"])
            self.assertEquals(each_expected_output, arguments._output_directory)

    def test_all_output_directory_stays_the_same(self):
        arguments = None
        with patch.object(Arguments, "_identifier", return_value="2"):
            arguments = Arguments(["foo/test.mad", "23"])
            self.assertEqual(arguments._output_directory, "test_2")

        with patch.object(Arguments, "_identifier", return_value="3"):
            self.assertEqual(arguments._output_directory, "test_2")
