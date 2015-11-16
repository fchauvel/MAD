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

from mad.mad import Mad, Controller, UI


class TestMAD(TestCase):

    def test_sensitivity_analysis(self):
        mad = MagicMock(Mad)
        controller = Controller(mad)
        controller.run(["-sa"])

        self.assertEqual(1, mad.sensitivity_analysis.call_count)

    def test_sandbox(self):
        mad = MagicMock(Mad)
        controller = Controller(mad)
        controller.run(["-sb"])

        self.assertEqual(1, mad.sandbox.call_count)

    def test_default_command(self):
        mad = MagicMock(Mad)
        controller = Controller(mad)
        controller.run([])

        self.assertEqual(1, mad.sensitivity_analysis.call_count)

    def test_unknown_command(self):
        mad = MagicMock(Mad)
        ui = MagicMock(UI)
        controller = Controller(mad, ui)
        controller.run(["--this-command-does-not-exist"])

        self.assertEqual(1, ui.unknown_command.call_count)


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
