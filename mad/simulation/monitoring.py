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

from mad.evaluation import Symbols
from mad.simulation.commons import SimulatedEntity


MISSING_VALUE = "NA"


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
        Probe("queue length", 4, "{:d}", lambda self: self._queue_length()),
        Probe("utilisation", 10, "{:5.2f}", lambda self: self._utilisation()),
        Probe("worker count", 4, "{:d}", lambda self: self._worker_count())
    ]

    def __init__(self, name, environment, period):
        super().__init__(name, environment)
        self.period = period or self.DEFAULT_PERIOD
        self.probes = self.DEFAULT_PROBES
        self.report = self.create_report(self._header_format())
        self.schedule.every(self.period, self.monitor)

    def set_probes(self, probes):
        assert len(probes) > 0, "Invalid monitoring: No probes given!"
        self.probes = probes
        self.report = self.create_report(self._header_format())

    def _header_format(self):
        return [(each_probe.name, "%s") for each_probe in self.probes]

    def monitor(self):
        observations = {}
        for each_probe in self.probes:
            observations[each_probe.name] = each_probe.formatted(self)
        self.report(**observations)

    def _queue_length(self):
        task_pool = self.look_up(Symbols.QUEUE)
        return task_pool.size

    def _utilisation(self):
        service = self.look_up(Symbols.SERVICE)
        return service.workers.utilisation

    def _worker_count(self):
        service = self.look_up(Symbols.SERVICE)
        return service.worker_count