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

from mad.experiments.sensitivity import ClientStub, ServiceStub
from mad.engine import CompositeAgent
from mad.server import Server
from mad.throttling import RandomEarlyDetection
from mad.scalability import UtilisationController


class Sandbox:

    def run(self):
        back_end = ServiceStub(15, rejection_rate=0.)

        server_B = Server("server_A", 0.15,
                          throttling=RandomEarlyDetection(30),
                          scalability=UtilisationController(70, 80, 1))
        server_B.back_ends = [ back_end ]

        server_A = Server("server_B", 0.15,
                          throttling=RandomEarlyDetection(20),
                          scalability=UtilisationController(70, 80, 1))
        server_A.back_ends = [ server_B ]

        client = ClientStub()
        client.server = server_A

        simulation = CompositeAgent("sandbox", client, server_A, server_B, back_end)
        simulation.setup()

        simulation.run_until(1000)