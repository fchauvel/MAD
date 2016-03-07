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

from mad.des2.ui import CommandLineInterface, Display
from mad.des2.repository import Repository


class TestUI(TestCase):

    def test_ui_behaviour(self):
        display = MagicMock(Display)
        repository = self._make_fake_repository()
        cli = CommandLineInterface(display, repository)

        cli.simulate("test.mad", 25)

        repository.load.assert_called_once_with("test.mad")

        display.simulation_started.assert_called_once_with()
        display.update.assert_has_calls([call(5), call(10), call(15), call(20), call(25)])
        display.simulation_complete.assert_called_once_with()

    def _make_fake_repository(self):
        repository = MagicMock(Repository)
        repository.load.return_value = self._make_fake_simulation()
        return repository

    def _make_fake_simulation(self):
        simulation = MagicMock()
        simulation.run_until = MagicMock()

        def run_simulation(limit, display):
            display.simulation_started()
            for i in range(1,6):
                display.update(i*5)
            display.simulation_complete()

        simulation.run_until.side_effect = run_simulation
        return simulation
