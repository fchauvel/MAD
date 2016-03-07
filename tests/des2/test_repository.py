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
from mad.des2.repository import Repository

from mock import MagicMock, mock_open, patch
from mad.des2.repository import Repository, Interpreter
from mad.des2.ast import Sequence, DefineService, DefineOperation, DefineClientStub, Think, Query


class RepositoryTests(TestCase):

    def test_loading(self):

        parser = self._make_fake_parser()
        interpreter = Interpreter()
        repository = Repository(parser, interpreter)

        simulation = repository.load("test.mad")

        self.assertTrue(parser.parse.called)
        self.assertEqual(len(simulation.services), 1)
        self.assertEqual(len(simulation.clients), 1)

    def _make_fake_parser(self):
        parser = MagicMock()
        parser.parse = MagicMock()
        parser.parse.return_value = \
            Sequence(
                DefineService("DB", DefineOperation("Select", Think(5))),
                DefineClientStub("Client", 10, Query("DB", "Select"))
            )
        return parser
