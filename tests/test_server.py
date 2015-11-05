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
from mock import MagicMock

from mad.engine import CompositeAgent
from mad.server import Server, Queue, Cluster, Meter
from mad.client import Client, Request
from mad.math import Constant


class ServerTest(TestCase):

    def test_server_responds_to_request(self):
        client = MagicMock(Client)
        server = Server("server", 0.1)
        server.setup()

        server.process(Request(client))
        server.process(Request(client))

        server.run_until(100)

        self.assertEqual(2, client.on_request_successful.call_count)

    def test_server_utilisation(self):
        client = MagicMock(Client)
        server = Server("server", 0.1)
        server.setup()

        server.process(Request(client))

        self.assertEqual(100, server.utilisation)
        server.run_until(20)

        self.assertEqual(0, server.utilisation)

    def test_server_queue_length(self):
        client = MagicMock(Client)
        server = Server("server", 0.1)
        server.setup()

        server.process(Request(client))
        server.process(Request(client))

        self.assertEqual(1, server.queue_length)
        server.run_until(50)

        self.assertEqual(0, server.queue_length)

    def test_setting_size_of_cluster(self):
        cluster = Cluster(Queue(), Meter(), 0.2)
        self.assertEqual(1, cluster.active_unit_count)

        cluster.active_unit_count = 4
        self.assertEqual(4, cluster.active_unit_count)

        cluster.active_unit_count = 2
        self.assertEqual(2, cluster.active_unit_count)

    def test_setting_negative_size_of_cluster(self):
        cluster = Cluster(Queue(), Meter(), 0.2)
        self.assertEqual(1, cluster.active_unit_count)

        cluster.active_unit_count = -100
        self.assertEqual(0, cluster.active_unit_count)


if __name__ == '__main__':
    main()

