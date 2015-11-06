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
from mock import MagicMock, PropertyMock

from mad.client import Client, Request
from mad.server import Server
from mad.sensitivity import ServiceStub, ClientStub


class TestServiceStub(TestCase):

    def test_response_time(self):
        server = ServiceStub(response_time=20, rejection_rate=0)
        server.on_start()

        def get_time():
            return server.current_time

        client = MagicMock(Client)
        type(client).current_time = PropertyMock(side_effect = get_time)

        request = Request(client)
        request.send_to(server)

        server.run_until(50)

        self.assertTrue(request.is_replied)
        self.assertEqual(20, request._completion_time)


class TestClientStub(TestCase):

    def test_emission_rate(self):
        server = MagicMock(Server)

        client = ClientStub(emission_rate=0.5)
        client.server = server

        client.run_until(100)

        self.assertEqual(50, server.process.call_count)