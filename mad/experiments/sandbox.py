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

from mad.des import CompositeAgent
from mad.client import ClientStub
from mad.server import Server, ServiceStub
from mad.throttling import TailDrop, RED, StaticThrottling
from mad.autoscaling import Controller, UtilisationThreshold, FixedCluster, Limited
from mad.backoff import ConstantDelay, FibonacciDelay, ExponentialBackOff
from mad.math import Constant, PerlinNoise


class Sandbox:

    def run(self):
        back_end = ServiceStub(response_time=15, rejection_rate=0)

        server_C = Server("server_C",
                          service_time=Constant(5),
                          throttling=TailDrop(15),
                          scalability=Controller(period=30, strategy=Limited(UtilisationThreshold(min=40, max=60, step=1), 10)),
                          back_off = ConstantDelay.factory)
        server_C._is_recording_active = True
        server_C.back_ends = [back_end]

        server_B = Server("server_B",
                          service_time=Constant(2),
                          throttling=TailDrop(15),
                          scalability=Controller(period=40, strategy=Limited(UtilisationThreshold(min=40, max=60, step=1), 30)),
                          back_off = ExponentialBackOff.factory)
        server_B._is_recording_active = True
        server_B.back_ends = [ server_C ]

        server_A = Server("server_A",
                          service_time=Constant(2),
                          throttling=TailDrop(15),
                          scalability=Controller(period=30, strategy=Limited(UtilisationThreshold(min=40, max=60, step=1), 30)),
                          back_off = ExponentialBackOff.factory)
        server_A.back_ends = [ server_B ]
        server_A._is_recording_active = True

        #oscillation = Cycle(GaussianNoise(Interpolation(10, [Point(0, 25), Point(200, 2), Point(400, 25)]), 5), 400)
        work_load = PerlinNoise(octave_count=5, persistence=1.75, base_resolution=3)
        clients = []
        for each_client in range(1, 20):
            client = ClientStub(name="Client %d" % each_client, inter_request_period=work_load)
            client.server = server_A
            clients.append(client)

        simulation = CompositeAgent("sandbox", server_A, server_B, server_C, back_end, *clients)
        simulation.setup()

        with open("sandbox.log", "w+") as trace:
            simulation.trace = trace
            simulation.run_until(2000, record_every=10)


if __name__ == "__main__":
    sandbox = Sandbox()
    sandbox.run()