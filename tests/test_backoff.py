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
from mock import patch

from mad.backoff import ExponentialBackOff


class TestExponentialBackOff(TestCase):

    def test_delay_factor(self):
        backoff = ExponentialBackOff(10)
        backoff.new_rejection()
        backoff.new_rejection()

        with patch("mad.backoff.randint", return_value=2):
            self.assertEqual(2*10, backoff.delay)

    def test_delay_factor_is_reset(self):
        backoff = ExponentialBackOff(10)
        backoff.new_rejection()
        backoff.new_rejection()
        backoff.new_success()

        self.assertEqual(0, backoff.delay)


if __name__ == "__main__":
    from unittest import main
    main()