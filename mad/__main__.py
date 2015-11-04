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
from mad.math import Constant, GaussianNoise

server = Server("server", 0.15,
                throttling=RandomEarlyDetection(25),
                scalability=UtilisationController(70, 80, 1))

clients = []
for i in range(20):
    client = Client("client %d" % i, GaussianNoise(Constant(0.2), variance=0.05))
    client.server = server
    clients.append(client)

simulation = CompositeAgent("simulation", server, *clients)

simulation.run_until(500)

