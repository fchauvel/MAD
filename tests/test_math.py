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

from unittest import TestCase, main
from mock import patch

from mad.math import Point, Constant, GaussianNoise, LowerBound, UpperBound, Interpolation, Cycle


class TestFunction(TestCase):

    def _verify_points(self, function, points):
        for (each_time, each_value) in points:
            self.assertEqual(each_value, function.value_at(each_time), "f(%d) != %d (found %d)" % (each_time, each_value, function.value_at(each_time)) )


class TestConstant(TestFunction):

    def test_constant_are_always_the_same(self):
        constant = Constant(25)

        self._verify_points(
            constant,
            [Point(1, 25), Point(10, 25), Point(100, 25)]
        )


class TestGaussianNoise(TestFunction):

    def test_noise(self):
        function = GaussianNoise(Constant(25))

        with patch.object(function, "_noise", return_value=3):
            self._verify_points(
                function,
                [Point(1, 28), Point(10, 28), Point(100, 28)]
            )


class TestInterpolation(TestFunction):

    def test_interpolation(self):
        function = Interpolation(default=20, points=[Point(0, 0), Point(10, 20)])
        self._verify_points(
            function,
            [Point(0, 0),
             Point(10, 20),
             Point(5, 10),
             Point(31, 20),
             Point(-1, 20)])


class TestCycle(TestFunction):

    def test_cycling(self):
        function = Cycle(Interpolation(20, [Point(0,0), Point(10, 10), Point(20, 0)]), 20)
        self._verify_points(
            function,
            [ Point(0, 0), Point(5, 5),
              Point(10, 10), Point(15, 5),
              Point(20, 0), Point(25, 5),
              Point(30, 10), Point(35, 5),
              Point(40, 0) ])


class TestLowerBound(TestCase):

    def test_range_check_use_lower_bound(self):
        function = LowerBound(Constant(5), 15)

        self.assertEqual(15, function.value_at(1))

    def test_range_check_do_not_use_lower_bound(self):
        function = LowerBound(Constant(5), 2)

        self.assertEqual(5, function.value_at(1))


class TestUpperBound(TestCase):

    def test_use_upper_bound(self):
        function = UpperBound(Constant(20), 15)

        self.assertEqual(15, function.value_at(1))

    def test_do_not_use_upper_bound(self):
        function = UpperBound(Constant(10), 15)

        self.assertEqual(10, function.value_at(1))


if __name__ == '__main__':
    main()




