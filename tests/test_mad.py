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

from io import StringIO

from mad.mad import Controller, UI, CommandFactory


class TestCommands(TestCase):

    def test_sandbox(self):
        controller = MagicMock(Controller)
        command = CommandFactory.parse_all(["-sb"])
        command.send_to(controller)
        self.assertTrue(controller.sandbox.called_once())

    def test_sensitivity_analysis(self):
        controller = MagicMock(Controller)
        command = CommandFactory.parse_all(["-sa"])
        command.send_to(controller)
        self.assertTrue(controller.sensitivity_analysis.called_once())

    def test_unknown_command(self):
        controller = MagicMock(Controller)
        command = CommandFactory.parse_all(["-unknown"])
        command.send_to(controller)
        self.assertTrue(controller.unknown_command.called_once())


class TestUI(TestCase):

    def test_printing_message(self):
        output = StringIO()
        ui = UI(output)
        ui.print("This is a message")

        self.assertEqual("This is a message\n", output.getvalue())

    def test_showing_message(self):
        output = StringIO()
        ui = UI(output)
        ui.show("This is a message")

        self.assertEqual("This is a message\r", output.getvalue())
