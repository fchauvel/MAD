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
from mad.scalability import UtilisationController


class UtilisationControllerTest(TestCase):

    def test_controller_decreases_cluster_size(self):
        cluster = MagicMock(Cluster)
        type(cluster).utilisation = PropertyMock(return_value=100)
        type(cluster).active_unit_count = PropertyMock(return_value=50)

        controller = UtilisationController(min=80, max=90, step=2)
        controller.cluster = cluster

        self.assertAlmostEqual(52, controller.signal, places=6)

    def test_controller_increases_cluster_size(self):
        cluster = MagicMock(Cluster)
        type(cluster).utilisation = PropertyMock(return_value=60)
        type(cluster).active_unit_count = PropertyMock(return_value=50)

        controller = UtilisationController(min=80, max=90, step=2)
        controller.cluster = cluster

        self.assertAlmostEqual(48, controller.signal, places=6)
