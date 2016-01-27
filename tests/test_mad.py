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
from mock import MagicMock, mock_open, patch

from io import StringIO

from mad.mad import UI, Controller, Repository, Builder
from mad.des import CompositeAgent
from mad.parsing import Parser


class TestController(TestCase):
    """
    Specification of the entry point of the program
    """
    def test_trigger_parsing_and_simulation(self):
        fake_simulation = MagicMock(CompositeAgent)
        fake_ui = MagicMock(UI)
        fake_repository = MagicMock(Repository)
        fake_builder = MagicMock(Builder)
        fake_builder.assemble.return_value = fake_simulation

        controller = Controller(fake_ui, fake_repository, fake_builder)
        controller.simulate(["system.mad", "environment.mad"])

        self.assertEqual(2, fake_repository.load.call_count)
        self.assertEqual(1, fake_builder.assemble.call_count)
        self.assertEqual(1, fake_simulation.run_until.call_count)


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


class TestRepository(TestCase):

    def test_parsing_file(self):
        source_file = "my_test_file.mad"
        mock = mock_open(read_data="architecture SensApp:")

        fake_parser = MagicMock(Parser)

        with patch('mad.mad.open', mock, create=True):
            repository = Repository(fake_parser)
            architecture = repository.load("my_test_file.mad")

        mock.assert_called_once_with('my_test_file.mad')
        self.assertEqual(1, fake_parser.parse.call_count)


