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
from mock import MagicMock, call
from io import StringIO
from re import search, IGNORECASE

from mad import __version__ as MAD_VERSION
from mad.des2.ui import CommandLineInterface, Display
from mad.des2.repository import Repository


class TestDisplay(TestCase):

    def setUp(self):
        self.output = StringIO()
        self.display = Display(self.output)

    def test_boot_up(self):
        self.display.boot_up()
        self._verify_output(MAD_VERSION)

    def test_simulation_started(self):
        path = "test.mad"
        self.display.simulation_started(path)
        self._verify_output(path)

    def test_simulation_update(self):
        self.display.update(20, 100)
        self._verify_output("20 %")

    def test_simulation_complete(self):
        self.display.simulation_complete()
        self._verify_output("complete")

    def _verify_output(self, expected_pattern):
        output = self.output.getvalue()
        self.assertTrue(search(expected_pattern, output, IGNORECASE), "Found %s" % output)


class TestUI(TestCase):

    def test_parsing_parameter(self):
        cli = CommandLineInterface(None, None)
        cli.simulate = MagicMock()

        cli.simulate_arguments(["test.mad", "25"])

        cli.simulate.assert_called_once_with("test.mad", 25)

    def test_detecting_missing_arguments(self):
        cli = CommandLineInterface(None, None)
        cli.simulate = MagicMock()

        with self.assertRaises(ValueError):
            cli.simulate_arguments([25])

    def test_detecting_wrong_arguments(self):
        cli = CommandLineInterface(None, None)
        cli.simulate = MagicMock()

        with self.assertRaises(ValueError):
            cli.simulate_arguments([25, "test.mad"])

        with self.assertRaises(ValueError):
            cli.simulate_arguments(["test.mad", "25x"])

    def test_ui_behaviour(self):
        display = MagicMock(Display)
        repository = self._make_fake_repository()
        cli = CommandLineInterface(display, repository)

        cli.simulate("test.mad", 25)

        repository.load.assert_called_once_with("test.mad")

        display.simulation_started.assert_called_once_with("test.mad")
        display.update.assert_has_calls([call(5, 25), call(10, 25), call(15, 25), call(20, 25), call(25, 25)])
        display.simulation_complete.assert_called_once_with()

    def _make_fake_repository(self):
        repository = MagicMock(Repository)
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
