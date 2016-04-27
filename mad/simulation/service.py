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
from mad.ast.actions import Think
from mad.evaluation import Symbols, Evaluation
from mad.simulation.commons import SimulatedEntity
from mad.simulation.workers import WorkerPool, Worker
from mad.simulation.tasks import Task


class Operation(SimulatedEntity):
    """
    Represent an operation exposed by a service
    """

    def __init__(self, name, parameters, body, environment):
        super().__init__(name, environment)
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return "operation:%s" % (str(self.body))

    def invoke(self, task, arguments, continuation=lambda r: r, worker=None):
        environment = self.environment.create_local_environment(worker.environment)
        environment.define(Symbols.TASK, task)
        environment.define_each(self.parameters, arguments)

        def compute_and_send_response(status):
            if task.request.kind == task.request.QUERY:
                return Evaluation(environment, Think(1), self.factory, lambda s: send_response(status)).result
            else:
                send_response(status)

        def send_response(status):
            if status.is_successful:
                if task.request.is_pending: # Could have timed out
                    task.request.reply_success()
                    self.listener.success_replied_to(task.request)
                else:
                    self.listener.error_replied_to(task.request)

            elif status.is_erroneous:
                task.request.reply_error()
                self.listener.error_replied_to(task.request)

            else:
                pass

            service = environment.look_up(Symbols.SELF)
            worker = environment.dynamic_look_up(Symbols.WORKER)
            service.release(worker)
            continuation(status) # TODO: Must be over! Remove this useless call to continuation

        return Evaluation(environment, self.body, self.factory, compute_and_send_response).result



class Service(SimulatedEntity):

    def __init__(self, name, environment):
        super().__init__(name, environment)
        self.environment.define(Symbols.SELF, self)
        self.environment.define(Symbols.SERVICE, self)
        self.tasks = self.environment.look_up(Symbols.QUEUE)
        self.workers = WorkerPool([self._new_worker(id) for id in range(1, 2)])

    def _new_worker(self, identifier):
        environment = self.environment.create_local_environment()
        environment.define(Symbols.SERVICE, self)
        return Worker(identifier, environment)

    @property
    def worker_count(self):
        return self.workers.capacity

    def set_worker_count(self, capacity):
        error = self.workers.capacity - capacity
        if error < 0:
            new_workers = [self._new_worker(id) for id in range(-error)]
            self.workers.add_workers(new_workers)
        elif error > 0:
            self.workers.shutdown(error)

    @property
    def utilisation(self):
        return self.workers.utilisation

    def process(self, request):
        self.listener.arrival_of(request)
        task = Task(request)
        if self.workers.are_available:
            request.accept()
            worker = self.workers.acquire_one()
            worker.assign(task)
        else:
            self.tasks.put(task)

    def release(self, worker):
        if self.tasks.are_pending:
            task = self.tasks.take()
            worker.assign(task)
        else:
            self.workers.release(worker)

    def activate(self, task):
        if self.workers.are_available:
            worker = self.workers.acquire_one()
            self.tasks.intercept(task)
            worker.assign(task)
        else:
            self.tasks.activate(task)

    def pause(self, task):
        self.tasks.pause(task)