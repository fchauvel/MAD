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

from mad.evaluation import Symbols, Evaluation
from mad.simulation.commons import SimulatedEntity
from mad.simulation.service import Operation
from mad.simulation.tasks import Task, TaskStatus
from mad.simulation.workers import Worker


class ClientRequest:

    def __init__(self):
        self.identifier = -1
        self.operation = Symbols.CLIENT_OPERATION
        self.priority = 0
        self.is_pending = True
        self.response_time = -1

    def accept(self):
        pass

    def finalise(self, task, status):
        if status.is_successful:
            task.succeed()
        else:
            task.fail()


class ClientStub(SimulatedEntity):

    def __init__(self, name, environment, period, body):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.environment.define(Symbols.SERVICE, self)
        self._define_operation(body)
        self.period = period

    def _define_operation(self, body):
        operation = Operation(Symbols.CLIENT_OPERATION, [], body, self.environment)
        self.environment.define(Symbols.CLIENT_OPERATION, operation)

    def initialize(self):
        self.schedule.every(self.period, self.invoke)

    def invoke(self):
        task = Task(self, ClientRequest())
        task.accept()
        task.assign_to(self._new_worker())

    def _new_worker(self):
        env = self.environment.create_local_environment(self.environment)
        worker = Worker(identifier=-1, environment=env)
        return worker

    def activate(self, task):
        task.activate()
        task.assign_to(self._new_worker())

    def pause(self, task):
        pass

    def release(self, worker):
        pass
