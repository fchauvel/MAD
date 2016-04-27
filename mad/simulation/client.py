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
from mad.simulation.tasks import Task


class Monitor:

    def __init__(self):
        self.success_count = 0
        self.error_count = 0

    def record_success(self):
        self.success_count += 1

    def record_error(self):
        self.error_count += 1


class ClientStub(SimulatedEntity):

    def __init__(self, name, environment, period, body):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.period = period
        self.body = body
        self.monitor = Monitor()

    def initialize(self):
        self.schedule.every(self.period, self.invoke)

    def invoke(self):
        def post_processing(result):
            if result.is_successful:
                self.on_success()
            elif result.is_erroneous:
                self.on_error()
            else:
                pass
        self.environment.define(Symbols.TASK, Task())
        env = self.environment.create_local_environment(self.environment)
        env.define(Symbols.WORKER, self)
        Evaluation(env, self.body, self.factory, post_processing).result

    def activate(self, task):
        task.resume(self)

    def pause(self, task):
        pass

    def release(self, worker):
        pass

    def on_success(self):
        self.monitor.record_success()

    def on_error(self):
        self.monitor.record_error()
