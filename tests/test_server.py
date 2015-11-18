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

from unittest import TestCase, main
from mock import MagicMock, PropertyMock

from mad.math import Constant
from mad.server import Server, ServiceStub
from mad.client import Client, Request


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


class ServerTest(TestCase):

    def test_server_forward_requests(self):
        back_ends = [MagicMock(Server), MagicMock(Server)]
        server = Server("server", Constant(10))
        server.back_ends = back_ends

        server.process(Request(MagicMock(Client)))
        server.run_until(100)

        for each_back_end in back_ends:
            self.assertEqual(1, each_back_end.process.call_count)

    def test_server_responds_to_request(self):
        client = MagicMock(Client)
        server = Server("server", Constant(10))
        server.on_start()

        server.process(Request(client))
        server.process(Request(client))

        server.run_until(100)

        self.assertEqual(2, client.on_completion_of.call_count)

    def test_server_utilisation(self):
        client = MagicMock(Client)
        server = Server("server", Constant(10))
        server.on_start()

        server.process(Request(client))

        self.assertEqual(100, server.utilisation)
        server.run_until(20)

        self.assertEqual(0, server.utilisation)

    def test_server_queue_length(self):
        client = MagicMock(Client)
        server = Server("server", Constant(10))
        server.on_start()

        server.process(Request(client))
        server.process(Request(client))

        self.assertEqual(1, server.queue_length)
        server.run_until(50)

        self.assertEqual(0, server.queue_length)

    def test_setting_size_of_cluster(self):
        cluster = Server("x", Constant(5))._cluster
        self.assertEqual(1, cluster.active_unit_count)

        cluster.active_unit_count = 4
        self.assertEqual(4, cluster.active_unit_count)

        cluster.active_unit_count = 2
        self.assertEqual(2, cluster.active_unit_count)

    def test_setting_negative_size_of_cluster(self):
        cluster = Server("x", Constant(5))._cluster
        self.assertEqual(1, cluster.active_unit_count)

        cluster.active_unit_count = -100
        self.assertEqual(0, cluster.active_unit_count)


if __name__ == '__main__':
    main()

