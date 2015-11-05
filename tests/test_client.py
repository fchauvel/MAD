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

from mad.client import Client, Meter, Request
from mad.server import Server
from mad.math import Constant


class ClientTest(TestCase):

    def test_client_emit_the_proper_number_of_request(self):

        def server_response(request):
            request.reply()

        client = Client("client", Constant(0.2))
        server = MagicMock(Server)
        server.process.side_effect = server_response
        client.server = server
        client.run_until(100)

        self.assertEqual(20, server.process.call_count)


class RequestTest(TestCase):

    def test_response_time(self):
        client = MagicMock(Client)
        type(client).current_time = PropertyMock(side_effect = [10, 20])
        server = MagicMock(Server)

        request = Request(client)
        request.send_to(server)
        request.reply()

        self.assertEqual(10, request.response_time)


class MeterTest(TestCase):

    def test_response_time(self):
        request = MagicMock(Request)
        type(request).response_time = PropertyMock(side_effect = [5, 15])
        meter = Meter()

        meter.new_success(request)
        meter.new_success(request)

        self.assertEqual(10, meter.average_response_time)

    def test_undefined_response_time(self):
        meter = Meter()

        self.assertEqual(Meter.NO_RESPONSE_TIME, meter.average_response_time)

    def test_rejection_count(self):
        meter = Meter()
        meter.new_rejection()
        meter.new_rejection()

        self.assertEqual(2, meter.rejection_count)

    def test_reset(self):
        meter = Meter()
        meter.new_rejection()
        meter.new_rejection()
        meter.reset()

        self.assertEqual(0, meter.rejection_count)



if __name__ == "__main__":
    main()