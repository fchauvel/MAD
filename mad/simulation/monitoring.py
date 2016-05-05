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

from functools import reduce

from mad.evaluation import Symbols
from mad.simulation.service import Operation
from mad.simulation.commons import SimulatedEntity
from mad.simulation.events import Listener
from mad.simulation.tasks import TaskStatus
from mad.simulation.client import ClientStub

MISSING_VALUE = "NA"


class TasksStatistics(Listener):

    def __init__(self):
        self.created = 0
        self.ready = 0
        self.running = 0
        self.blocked = 0
        self.rejected = 0
        self.successful = 0
        self.failed = 0

    def task_created(self, request):
        self.created += 1

    def task_activated(self, task):
        if task.status == TaskStatus.CREATED:
            self.created -= 1
            self.ready += 1
        elif task.status == TaskStatus.BLOCKED:
            self.blocked -= 1
            self.ready += 1
        else:
            error = "Invalid task status (expected CREATED or BLOCKED, found {!s})".format(task.status)
            raise AssertionError(error)

    def task_accepted(self, task):
        pass

    def task_rejected(self, task):
        assert task.status == TaskStatus.CREATED, "Invalid task status (expected CREATED, found {!s})".format(task.status)
        self.created -= 1
        self.rejected += 1

    def task_assigned_to(self, task, worker):
        if task.status == TaskStatus.CREATED:
            self.created -= 1
            self.running += 1
        elif task.status == TaskStatus.READY:
            self.ready -= 1
            self.running += 1
        else:
            message = "Invalid task status (expected CREATED or BLOCKED, found {!s})".format(task.status)
            raise AssertionError(message)

    def task_paused(self, task):
        assert task.status == TaskStatus.RUNNING, "Invalid task status (expected BLOCKED, found {!s})".format(task.status)
        self.blocked += 1
        self.running -= 1

    @property
    def active(self):
        return self.created + \
               self.ready + \
               self.running + \
               self.blocked

    @property
    def complete(self):
        return self.successful + self.failed

    def task_successful(self, request):
        assert self.running > 0, "No task can succeed as none is running (State: {!s})".format(self)
        self.running -= 1
        self.successful += 1

    def task_failed(self, request):
        assert self.running > 0, "No task can fail as none is running (State: {!s})".format(self)
        self.running -= 1
        self.failed += 1

    def task_cancelled(self, task):
        pass

    def failure_of(self, request):
        pass

    def success_of(self, request):
        pass

    def posting_of(self, service, request):
        pass

    def acceptance_of(self, request):
        pass

    def resuming(self, request):
        pass

    def timeout_of(self, request):
        pass

    def rejection_of(self, request):
        pass

    def __repr__(self):
        return "(C={0.created:d}, Rd={0.ready:d}, Rn={0.running:d}, B={0.blocked:d}| " \
               "S={0.successful:d}, F={0.failed:d})".format(self)


class OperationStatistics:

    def __init__(self):
        self.call_count = 0
        self.error_count = 0
        self.rejection_count = 0
        self.response_times = []

    def reset(self):
        self.__init__()

    def call(self):
        self.call_count += 1

    def call_rejected(self):
        self.rejection_count += 1

    def call_failed(self):
        self.error_count += 1

    def call_succeed(self, duration):
        self.response_times.append(duration)

    @property
    def complete_call_count(self):
        return self.success_count + self.failure_count

    @property
    def success_count(self):
        return len(self.response_times)

    @property
    def failure_count(self):
        return self.rejection_count + self.error_count

    @property
    def reliability(self):
        total = self.complete_call_count
        if total == 0:
            return None
        else:
            return self.success_count / total

    @property
    def response_time(self):
        if len(self.response_times) == 0:
            return None
        else:
            return sum(self.response_times) / len(self.response_times)


class Statistics(Listener):

    def __init__(self):
        super().__init__()
        self.total_request_count = 0
        self._operations = {}

    def reset(self):
        self._operations.clear()

    def _get(self, operation_name):
        operation = self._operations.get(operation_name)
        if operation is None:
            operation = OperationStatistics()
            self._operations[operation_name] = operation
        return operation

    @property
    def reliability(self):
        total = self.complete_request_count
        if total == 0:
            return None
        return self.success_count / total

    @property
    def complete_request_count(self):
        counts = (each_operation.complete_call_count for each_operation in self._operations.values())
        return reduce(lambda x,y: x+y, counts, 0)

    @property
    def arrival_count(self):
        counts = (each_operation.call_count for each_operation in self._operations.values())
        return reduce(lambda x,y: x+y, counts, 0)

    @property
    def rejection_count(self):
        counts = (each_operation.rejection_count for each_operation in self._operations.values())
        return reduce(lambda x,y: x+y, counts, 0)

    @property
    def success_count(self):
        counts = (each_operation.success_count for each_operation in self._operations.values())
        return reduce(lambda x,y: x+y, counts, 0)

    @property
    def failure_count(self):
        counts = (each_operation.failure_count for each_operation in self._operations.values())
        return reduce(lambda x,y: x+y, counts, 0)

    @property
    def response_time(self):
        (total, count) = (0, 0)
        for (operation, statistics) in self._operations.items():
            total += sum(statistics.response_times)
            count += len(statistics.response_times)
        if count <= 0:
            return None
        else:
            return total / count

    def response_time_for(self, operation):
        return self._get(operation).response_time

    def reliability_for(self, operation):
        return self._get(operation).reliability

    def request_count_for(self, operation):
        return self._get(operation).call_count

    # Event handlers

    def task_created(self, task):
        self.total_request_count += 1
        self._get(task.request.operation).call()

    def task_accepted(self, task):
        pass

    def task_rejected(self, task):
        self._get(task.request.operation).call_rejected()

    def task_assigned_to(self, task, worker):
        pass

    def task_paused(self, task):
        pass

    def task_activated(self, task):
        pass

    def task_failed(self, task):
        self._get(task.request.operation).call_failed()

    def task_successful(self, task):
        self._get(task.request.operation).call_succeed(task.request.response_time)

    def task_cancelled(self, task):
        pass

    def resuming(self, request):
        pass



    # Client side events

    def posting_of(self, service, request):
        pass

    def acceptance_of(self, request):
        pass

    def rejection_of(self, request):
        pass

    def success_of(self, request):
        pass

    def failure_of(self, request):
        pass

    def timeout_of(self, request):
        pass


class Probe:

    def __init__(self, name, width, format, probe):
        self.name = name
        self.width = width
        self.format = format
        self.probe = probe

    def formatted(self, context):
        return ("{:>%d}" % self.width).format(self._as_text(context))

    def _as_text(self, context):
        value = self.measure(context)
        if value is None:
            return "{:s}".format(MISSING_VALUE)
        else:
            return self.format.format(value)

    def measure(self, context):
        return self.probe(context)


class Monitor(SimulatedEntity):
    """
    Monitors the various metrics from other components of the services (task pool, worker pool, etc.) and reports on
    a fixed period
    """
    DEFAULT_PERIOD = 10

    DEFAULT_PROBES = [
        Probe("time", 6, "{:d}", lambda self: self.schedule.time_now),
        Probe("queue", 4, "{:d}", lambda self: self._queue_length()),
        Probe("queue blocked", 4, "{:d}", lambda self: self._queue_blocked()),
        Probe("utilisation", 10, "{:5.2f}", lambda self: self._utilisation()),
        Probe("worker count", 4, "{:d}", lambda self: self._worker_count()),
        Probe("arrival rate", 10, "{:5.2f}", lambda self: self._arrival_rate()),
        Probe("rejection rate", 10, "{:5.2f}", lambda self: self._rejection_rate()),
        Probe("reliability", 10, "{:5.2f}", lambda self: self._reliability()),
        Probe("throughput", 10, "{:5.2f}", lambda self: self._throughput()),
        Probe("response time", 10, "{:5.2f}", lambda self: self._response_time())
    ]

    def __init__(self, name, environment, period):
        super().__init__(name, environment)
        self.period = period or self.DEFAULT_PERIOD
        self.probes = list(self.DEFAULT_PROBES)
        self._add_custom_probes()
        self.report = self._create_report(self._header_format())
        self.statistics = Statistics()
        self.tasks = TasksStatistics()
        self.listener.register(self.tasks)
        self.listener.register(self.statistics)
        self.schedule.every(self.period, self.monitor)

    def _add_custom_probes(self):
        for each_operation in self._all_operations():
            self._add_response_time(each_operation)
            self._add_reliability(each_operation)
            self._add_arrival_rate(each_operation)

    def _add_response_time(self, operation):
        response_time = Probe("response time " + operation.name,
                          10,
                          "{:5.2f}",
                          lambda self: self.statistics.response_time_for(operation.name))
        self.probes.append(response_time)

    def _add_reliability(self, operation):
        reliability = Probe("reliability " + operation.name,
                          10,
                          "{:5.2f}",
                          lambda self: self.statistics.reliability_for(operation.name))
        self.probes.append(reliability)

    def _add_arrival_rate(self, operation):
        arrival_rate = Probe("arrival rate " + operation.name,
                          10,
                          "{:5.2f}",
                          lambda self: self.statistics.request_count_for(operation.name) / self.period)
        self.probes.append(arrival_rate)

    def _all_operations(self):
        for (symbol, entity) in self.environment.bindings.items():
            if isinstance(entity, Operation):
                yield entity

    def set_probes(self, probes):
        assert len(probes) > 0, "Invalid monitoring: No probes given!"
        self.probes = probes
        self.report = self._create_report(self._header_format())

    def _create_report(self, format):
        name = self.look_up(Symbols.SERVICE).name
        return self.simulation._storage.report_for(name, format)

    def _header_format(self):
        return [(each_probe.name, "%s") for each_probe in self.probes]

    def monitor(self):
        observations = {}
        for each_probe in self.probes:
            observations[each_probe.name] = each_probe.formatted(self)
        self.report(**observations)
        self.statistics.reset()

    def _queue_length(self):
        return self.tasks.active

    def _queue_blocked(self):
        return self.tasks.blocked

    def _utilisation(self):
        service = self.look_up(Symbols.SERVICE)
        if isinstance(service, ClientStub): return None #TODO: Fix this ugly patch
        return service.workers.utilisation

    def _worker_count(self):
        service = self.look_up(Symbols.SERVICE)
        if isinstance(service, ClientStub): return None # TODO Fix this ugly patch
        return service.worker_count

    def _arrival_rate(self):
        return self.statistics.arrival_count / self.period

    def _rejection_rate(self):
        return self.statistics.rejection_count / self.period

    def _reliability(self):
        return self.statistics.reliability

    def _throughput(self):
        return self.statistics.success_count / self.period

    def _response_time(self):
        return self.statistics.response_time


class Logger(SimulatedEntity, Listener):
    REQUEST_RECEIVED = "Task {request:d} received"
    TASK_ACTIVATED = "Task {task:d} activated"
    TASK_PAUSED = "Task {task:d} paused"
    TASK_ASSIGNED = "Task {task:d} assigned to Worker {worker:d}"
    ERROR_REPLIED = "Reply to Task. {request:d} (ERROR)"
    SUCCESS_REPLIED = "Reply to Task. {request:d} (SUCCESS)"

    REQUEST_SENT = "Req. {request:d} sent to {service:s}::{operation:s}"
    REQUEST_ACCEPTED = "Req. {request:d} accepted"
    REQUEST_REJECTED = "Req. {request:d} rejected!"
    REQUEST_TIMEOUT = "Req. {request:d} timeout!"
    REQUEST_FAILURE = "Req. {request:d} failed!"
    REQUEST_SUCCESS = "Req. {request:d} successful"

    def __init__(self, environment):
        SimulatedEntity.__init__(self, Symbols.LOGGER, environment)
        Listener.__init__(self)
        self.listener.register(self)

    def resuming(self, request):
        pass

    def task_accepted(self, task):
        pass

    def task_rejected(self, task):
        pass

    def task_created(self, request):
        self._log(self.REQUEST_RECEIVED, request=request.identifier)

    def task_assigned_to(self, task, worker):
        self._log(self.TASK_ASSIGNED, task=task.identifier, worker=worker.identifier)

    def task_paused(self, task):
        self._log(self.TASK_PAUSED, task=task.identifier)

    def task_activated(self, task):
        self._log(self.TASK_ACTIVATED, task=task.identifier)

    def task_failed(self, task):
        self._log(self.ERROR_REPLIED, request=task.identifier)

    def task_successful(self, request):
        self._log(self.SUCCESS_REPLIED, request=request.identifier)

    def task_cancelled(self, task):
        pass

    def failure_of(self, request):
        self._log(self.REQUEST_FAILURE, request=request.identifier)

    def success_of(self, request):
        self._log(self.REQUEST_SUCCESS, request=request.identifier)

    def posting_of(self, service, request):
        self._log(self.REQUEST_SENT, request=request.identifier, service=service, operation=request.operation)

    def acceptance_of(self, request):
        self._log(self.REQUEST_ACCEPTED, request=request.identifier)

    def rejection_of(self, request):
        self._log(self.REQUEST_REJECTED, request=request.identifier)

    def timeout_of(self, request):
        self._log(self.REQUEST_TIMEOUT, request=request.identifier)

    def _log(self, message, **values):
        now = self.schedule.time_now
        caller = self.look_up(Symbols.SELF)
        self.simulation.log.record(now, caller.name, message.format(**values))
