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

from mad.des2.log import Log


class LogTests(TestCase):

    def setUp(self):
        self.log = Log()

    def test_record(self):
        self.assertTrue(self.log.is_empty)
        self.log.record(5, "S1", "something")
        self.assertFalse(self.log.is_empty)

    def test_size(self):
        self.assertTrue(self.log.is_empty)
        self.log.record(5, "X", "something")
        self.log.record(10, "X", "something else")
        self.assertEqual(self.log.size, 2)