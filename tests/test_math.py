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
from mock import MagicMock, patch

from mad.math import Point, Function, Constant, GaussianNoise, LowerBound, UpperBound, Interpolation


class TestConstant(TestCase):

    def test_constant_are_always_the_same(self):
        constant = Constant(25)

        self.assertEqual(25, constant.value_at(1))
        self.assertEqual(25, constant.value_at(10))
        self.assertEqual(25, constant.value_at(100))


class TestGaussianNoise(TestCase):

    def test_noise(self):
        noisy_function = GaussianNoise(Constant(25))

        with patch.object(noisy_function, "_noise", return_value=3):
            self.assertEqual(28, noisy_function.value_at(1))
            self.assertEqual(28, noisy_function.value_at(10))
            self.assertEqual(28, noisy_function.value_at(100))


class TestInterpolation(TestCase):

    def test_interpolation(self):
        function = Interpolation(default=20, points=[Point(0, 0), Point(10, 20)])
        self.assertEqual(0, function.value_at(0))
        self.assertEqual(20, function.value_at(10))
        self.assertEqual(10, function.value_at(5))
        self.assertEqual(20, function.value_at(31))
        self.assertEqual(20, function.value_at(-1))


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




