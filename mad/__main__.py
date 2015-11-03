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

from mad.engine import CompositeAgent
from mad.server import Server
from mad.client import Client
from mad.throttling import RandomEarlyDetection
from mad.scalability import UtilisationController


server = Server("server", 0.1, scalability=UtilisationController(60, 80, 1))
client = Client("client", 0.2)
client.server = server

simulation = CompositeAgent("simulation", client, server)

simulation.run_until(500)

