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

from mad.simulation.events import Listener, Dispatcher


FAKE_REQUEST = "whatever"


class DispatcherTests(TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher()

    def test_register_rejects_non_listener(self):
        with self.assertRaises(AssertionError):
            self.dispatcher.register("this is not a listener")

    def test_notifies_only_once_despite_multiple_registration(self):
        listener = self._fake_listener()
        self.dispatcher.register(listener)
        self.dispatcher.register(listener)

        self.dispatcher.arrival_of(FAKE_REQUEST)

        listener.arrival_of.assert_called_once_with(FAKE_REQUEST)

    def test_dispatch(self):
        invocations = [
            ("arrival_of", [FAKE_REQUEST]),
            ("rejection_of", [FAKE_REQUEST]),
            ("posting_of", [FAKE_REQUEST]),
            ("success_of", [FAKE_REQUEST]),
            ("failure_of", [FAKE_REQUEST]),
            ("timeout_of", [FAKE_REQUEST])
        ]

        for (method_name, parameters) in invocations:
            self._do_test_dispatch_of(method_name, *parameters)

    def _do_test_dispatch_of(self, method_name, *parameters):
        listener = self._fake_listener()

        method = getattr(self.dispatcher, method_name)
        method(*parameters)

        delegate = getattr(listener, method_name)
        delegate.assert_called_once_with(FAKE_REQUEST)

    def _fake_listener(self):
        listener = MagicMock(Listener)
        self.dispatcher.register(listener)
        return listener
