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

from mad.des import Agent, CompositeAgent, Action, RecorderBroker
from mad.server import Server, ServiceStub
from mad.client import Request, ClientStub
from mad.throttling import TailDrop
from mad.autoscaling import Controller, UtilisationThreshold
from mad.backoff import ConstantDelay
from mad.math import Constant, GaussianNoise


class Simulation(CompositeAgent):
    """
    The simulation that is run during the sensitivity analysis
    """

    def __init__(self):
        super().__init__("simulation")
        self._back_end = ServiceStub(response_time=10, rejection_rate=0.)
        self._server = Server("server",
                              service_time=Constant(2),
                              throttling=TailDrop(20),
                              scalability=Controller(period=40, strategy=UtilisationThreshold(70, 80, 1)),
                              back_off=ConstantDelay.factory)
        self._server._is_recording_active = True
        self._server.back_ends = [self._back_end]

        self._client = ClientStub(name="client", inter_request_period=GaussianNoise(Constant(5), 5))
        self._client.server = self._server

    @CompositeAgent.agents.getter
    def agents(self):
        return [self._back_end, self._server, self._client]

    @property
    def server(self):
        return self._server

    @property
    def client(self):
        return self._client

    @property
    def back_end(self):
        return self._back_end


class SensitivityAnalysisController:
    """
    A controller (as in Model-View-Controller) for the Sensitivity Analysis
    """

    def __init__(self, ui):
        self._ui = ui

    def execute(self):
        analysis = SensitivityAnalysis(listener=self)
        analysis.run_count = 100
        analysis.parameters = [ RejectionRate(), ResponseTime(), ClientRequestRate() ]
        analysis.run()

    def sensitivity_of(self, parameter, value, run):
        self._ui.show(" - %s: %.2f (Run %3d)" % (parameter.name, value, run))

    def sensitivity_analysis_complete(self, parameter):
        self._ui.print(" - %s ... DONE                  " % parameter.name)


class SensitivityAnalysis:
    """
    A sensitivity analysis that varies all input parameter, one at a time.
    """

    def __init__(self, listener):
        assert listener, "no listener given"
        self._run_count = 10
        self._parameters = {}
        self._simulation_end = 1000
        self._listener = listener

    @property
    def parameters(self):
        return self._parameters

    def parameters(self, new_parameters):
        self._parameters = {each_parameter.name: each_parameter for each_parameter in new_parameters}

    @property
    def run_count(self):
        return self._run_count

    @run_count.setter
    def run_count(self, new_count):
        self._run_count = new_count

    def run(self):
        for each_parameter in self.parameters:
            recorders = RecorderBroker(prefix=each_parameter.name)
            for each_value in each_parameter.domain:
                for each_run in range(self.run_count):
                    self.one_run(recorders, each_parameter, each_value, each_run)
            recorders.close_all()
            self._listener.sensitivity_analysis_complete(each_parameter)

    def one_run(self, recorders, parameter, value, run):
        self._listener.sensitivity_of(parameter, value, run)
        simulation = Simulation()
        simulation.recorders = recorders
        simulation.parameters = [
            ("subject", parameter.format, value),
            ("run", "%d", run)
        ]
        parameter.setup(value, simulation)
        simulation.setup()
        simulation.run_until(self._simulation_end, record_every=20)


class Parameter:
    """
    A parameter to be varied in a sensitivity analysis
    """

    def __init__(self, name, format, min, max, step, scaling=lambda x: x):
        self._name = name
        self._format = format
        self._lower_bound = min
        self._upper_bound = max
        self._step = step
        self._scaling = scaling

    @property
    def name(self):
        return self._name

    @property
    def format(self):
        return self._format

    @property
    def domain(self):
        current = self._lower_bound
        while current <= self._upper_bound:
            yield self._scaling(current)
            current += self._step

    def setup(self, value, simulation):
        pass


class RejectionRate(Parameter):

    def __init__(self):
        super().__init__("back end rejection rate", "%.2f", 0, 100, 10, scaling=lambda x: x/100)

    def setup(self, value, simulation):
        simulation.back_end.rejection_rate = value


class ResponseTime(Parameter):

    def __init__(self):
        super().__init__("back end response time", "%d", 5, 20, 2)

    def setup(self, value, simulation):
        simulation.back_end.response_time = value


class ClientRequestRate(Parameter):

    def __init__(self):
        super().__init__("client emission time", "%.2f", 1, 50, 5)

    def setup(self, value, simulation):
        simulation.client.inter_request_period = GaussianNoise(Constant(value), 5)


