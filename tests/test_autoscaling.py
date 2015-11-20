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

from unittest import TestCase
from mock import MagicMock, PropertyMock

from mad.server import Cluster
from mad.autoscaling import Controller, FixedCluster, UtilisationThreshold, Limited


class UtilisationThresholdTest(TestCase):

    @staticmethod
    def prepare_cluster(utilisation, size):
        cluster = MagicMock(Cluster)
        type(cluster).utilisation = PropertyMock(return_value=utilisation)
        type(cluster).active_unit_count = PropertyMock(return_value=size)
        return cluster

    def test_controller_increases_cluster_size(self):
        strategy = UtilisationThreshold(min=80, max=90, step=2)
        strategy.cluster = self.prepare_cluster(100, 50)
        self.assertAlmostEqual(52, strategy.control_signal, places=6)

    def test_controller_decreases_cluster_size(self):
        controller = UtilisationThreshold(min=80, max=90, step=2)
        controller.cluster = self.prepare_cluster(60, 50)
        self.assertAlmostEqual(48, controller.control_signal, places=6)


class TestLimited(TestCase):

    @staticmethod
    def fake_controller(control_signal):
        controller = MagicMock(Controller)
        type(controller).control_signal = PropertyMock(return_value = control_signal)
        return controller

    def test_signal_within_limits(self):
        sut = Limited(self.fake_controller(15), 20)
        self.assertEqual(15, sut.control_signal)

    def test_signal_outside_limits(self):
        sut = Limited(self.fake_controller(25), 20)
        self.assertEqual(20, sut.control_signal)

    def test_setting_cluster(self):
        strategy = FixedCluster(34)
        cluster = MagicMock(Cluster)
        limited = Limited(strategy, 10)
        limited.cluster = cluster
        self.assertIs(cluster, strategy.cluster)
        self.assertIs(cluster, limited.cluster)


class TestController(TestCase):

    def test_setting_cluster(self):
        cluster = MagicMock(Cluster)
        strategy = MagicMock(FixedCluster)
        controller = Controller(10, strategy)
        controller.cluster = cluster

        self.assertIs(cluster, strategy.cluster)
        self.assertIs(cluster, controller.cluster)

    def test_triggering_through_decorator(self):
        strategy = MagicMock(FixedCluster)
        mock = PropertyMock(return_value=25)
        type(strategy).control_signal = mock
        controller = Controller(10, Limited(strategy, 10))
        controller.cluster = MagicMock(Cluster)
        controller.run_until(100)

        self.assertEqual(10, mock.call_count)
