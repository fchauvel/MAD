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

from mock import MagicMock, call

from mad import __version__ as MAD_VERSION
from mad.datasource import Mad, Project
from mad.ui import CommandLineInterface, Display, Arguments


class DisplayTest(TestCase):

    def setUp(self):
        self.project = Project("sample/test.mad", 25)
        self.output = StringIO()
        self.display = Display(self.output)

    def test_boot_up(self):
        self.display.boot_up()
        self._verify_output(MAD_VERSION)

    def test_simulation_started(self):
        self.display.simulation_started(self.project)
        self._verify_output(self.project.file_name)

    def test_simulation_update(self):
        self.display.update(20, 100)
        self._verify_output("20.00 %")

    def test_simulation_complete(self):
        self.display.simulation_complete(self.project)
        self._verify_output(self.project.output_directory)

    def _verify_output(self, expected_pattern):
        output = self.output.getvalue()
        match = search(escape(expected_pattern), output, IGNORECASE)
        self.assertIsNotNone(match, msg="Could not find '%s' in output '%s'" % (expected_pattern, output))

    def test_ui_behaviour(self):
        display = MagicMock(Display)
        mad = self._make_fake_repository()
        cli = CommandLineInterface(display, mad)

        project = Project("test.mad", 25)
        cli.simulate(project)

        mad.load.assert_called_once_with(project)

        display.simulation_started.assert_called_once_with(project)
        display.update.assert_has_calls([call(5, 25), call(10, 25), call(15, 25), call(20, 25), call(25, 25)])
        display.simulation_complete.assert_called_once_with(project)

    def _make_fake_repository(self):
        repository = MagicMock(Mad)
        repository.load.return_value = self._make_fake_simulation()
        return repository

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
        project = Arguments(["test.mad", "25"]).as_project
        self.assertEqual("test.mad", project.file_name)
        self.assertEqual(25, project.limit)

    def test_detecting_missing_arguments(self):
        with self.assertRaises(ValueError):
            Arguments([25]).as_project

    def test_detecting_wrong_arguments(self):
        with self.assertRaises(ValueError):
            Arguments([25, "test.mad"]).as_project

        with self.assertRaises(ValueError):
            Arguments(["test.mad", "25x"]).as_project