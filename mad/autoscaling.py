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

from mad.simulation import Agent, Action


class AutoScalingStrategy:
    """
    The behaviour of auto-scaling strategies
    """

    def __init__(self):
        self._cluster = None

    @property
    def cluster(self):
        return self._cluster

    @cluster.setter
    def cluster(self, new_cluster):
        self._cluster = new_cluster

    @property
    def control_signal(self):
        pass


class FixedCluster(AutoScalingStrategy):
    """
    A "does-nothing" control strategy. Returns the current number of units in the cluster
    """

    def __init__(self, cluster_size=10):
        super().__init__()
        self._cluster_size = cluster_size

    @AutoScalingStrategy.control_signal.getter
    def control_signal(self):
        return self._cluster_size


class UtilisationThreshold(AutoScalingStrategy):
    """
    Control the number of active processing units
    """

    def __init__(self, min, max, step):
        super().__init__()
        self._min = min
        self._max = max
        self._step = step

    @AutoScalingStrategy.control_signal.getter
    def control_signal(self):
        if self.is_too_low():
            return self.remove_units()
        elif self.is_too_high():
            return self.add_units()
        else:
            return self.cluster.active_unit_count

    def is_too_high(self):
        return self.cluster.utilisation > self._max

    def is_too_low(self):
        return self.cluster.utilisation < self._min

    def add_units(self):
        return round(self.cluster.active_unit_count + self._step)

    def remove_units(self):
        return round(self.cluster.active_unit_count - self._step)

    def __str__(self):
        return "[%d, %d] %d -> %d" % (self._min, self._max, self.cluster.active_unit_count, self._step)


class Limited(AutoScalingStrategy):
    """
    Limit the control signal to a given range [0, capacity]
    """

    def __init__(self, delegate, capacity):
        super().__init__()
        self._capacity = capacity
        self._delegate = delegate

    @property
    def cluster(self):
        return self._delegate.cluster

    @cluster.setter
    def cluster(self, new_cluster):
        self._delegate.cluster = new_cluster

    @AutoScalingStrategy.control_signal.getter
    def control_signal(self):
        response = self._delegate.control_signal
        if response < self._capacity:
            return response
        return self._capacity




class Control(Action):
    """
    An action that triggers the auto-scaling
    """

    def __init__(self, subject):
        super().__init__()
        self._subject = subject

    def fire(self):
        self._subject.control()

    def __str__(self):
        return "Scaling"


class Controller(Agent):
    """
    Adjust the number of processing unit in a cluster at a fixed frequency
    """

    def __init__(self, period=10, strategy=FixedCluster()):
        super().__init__("scalability controller")
        self._control_period = period
        self._strategy = strategy

    @property
    def cluster(self):
        return self._strategy.cluster

    @cluster.setter
    def cluster(self, cluster):
        self._strategy.cluster = cluster

    def on_start(self):
        self.schedule_next_control()

    def schedule_next_control(self):
        self.schedule_in(Control(self), self._control_period)

    def control(self):
        assert self._strategy, "No auto-scaling strategy defined"
        assert self.cluster, "No cluster attached"
        new_signal = self._strategy.control_signal
        self.log("Unit Count = %d" % new_signal)
        self.cluster.active_unit_count = new_signal
        self.schedule_next_control()


