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
from mad.simulation import CompositeAgent
from mad.server import Server
from mad.throttling import RandomEarlyDetection, TailDrop
from mad.scalability import UtilisationController
from mad.backoff import ConstantDelay, FibonacciDelay


class Sandbox:

    def run(self):
        back_end = ServiceStub(15, rejection_rate=0.)

        server_C = Server("server_C", 0.15,
                          throttling=TailDrop(30),
                          scalability=UtilisationController(70, 80, 1))
        server_C.back_ends = [back_end]

        server_B = Server("server_B", 0.15,
                          throttling=TailDrop(15),
                          scalability=UtilisationController(70, 80, 1))
        server_B.back_ends = [ server_C ]

        server_A = Server("server_A", 0.15,
                          throttling=RandomEarlyDetection(20),
                          scalability=UtilisationController(70, 80, 2),
                          back_off = FibonacciDelay.factory)
        server_A.back_ends = [ server_B ]

        clients = []
        for each_client in range(1, 10):
            client = ClientStub(emission_rate=0.1)
            client.server = server_A
            clients.append(client)

        simulation = CompositeAgent("sandbox", server_A, server_B, server_C, back_end, *clients)
        simulation.setup()

        simulation.run_until(1000)