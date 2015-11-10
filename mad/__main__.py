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

from mad.engine import CompositeAgent, RecorderBroker
from mad.server import Server
from mad.throttling import RandomEarlyDetection, StaticThrottling
from mad.scalability import UtilisationController, FixedCluster
from mad.sensitivity import ServiceStub, ClientStub


def create_simulation():
    back_end = ServiceStub(15, rejection_rate)

    server = Server("server", 0.15,
                    throttling=RandomEarlyDetection(25),
                    scalability=UtilisationController(70, 80, 1))
    server.back_ends = [back_end]

    client = ClientStub(emission_rate=0.5)
    client.server = server

    return CompositeAgent("simulation", back_end, server, client)



recorders = RecorderBroker()

for each_value in range(0, 101, 5):
    rejection_rate = each_value / 100
    for run in range(0, 100):
        print("\rRejection rate: %.2f ; Run %d" % (rejection_rate, run), end="")

        simulation = create_simulation()
        simulation.parameters = [
            ("rejection_rate", "%f", rejection_rate),
            ("run", "%d", run)
        ]
        simulation.recorders = recorders
        simulation.setup()
        simulation.run_until(500)

simulation.teardown()