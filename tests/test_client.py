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

from mad.client import Client
from mad.server import Server


class ClientTest(TestCase):

    def test_client_emit_the_proper_number_of_request(self):
        client = Client("client", 0.2)
        server = MagicMock(Server)
        client.server = server
        client.run_until(100)

        self.assertEqual(20, server.process.call_count)


if __name__ == "__main__":
    main()