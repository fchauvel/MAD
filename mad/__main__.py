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
from mad.throttling import RandomEarlyDetection, StaticThrottling
from mad.scalability import UtilisationController, FixedCluster
from mad.sensitivity import ServiceStub, ClientStub

back_end = ServiceStub(response_time=15, rejection_rate=0.75)

server = Server("server", 0.15,
                throttling=RandomEarlyDetection(25),
                scalability=UtilisationController(70, 80, 1))
server.back_ends = [back_end]

client = ClientStub(emission_rate=0.5)
client.server = server

simulation = CompositeAgent("simulation", back_end, server, client)

simulation.run_until(500)

