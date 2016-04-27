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

from mad.simulation.requests import Request


class RequestTests(TestCase):

    def test_response_time(self):
        examples = [{"sent_at": 10, "replied_at": 26},
                    {"sent_at": 10, "replied_at": 11},
                    {"sent_at": 10, "replied_at": 12},
                    {"sent_at": 10, "replied_at": 100}]

        for each_example in examples:
            self.do_test_response_time(**each_example)

    def do_test_response_time(self, sent_at, replied_at):
        sender = MagicMock()
        type(sender.schedule).time_now = PropertyMock(side_effect = [sent_at, replied_at] )
        request = Request(sender, 0, "foo_operation", 1)

        recipient = MagicMock()

        request.send_to(recipient)
        request.reply_success()

        self.assertEqual(replied_at - sent_at, request.response_time)

    def test_response_time_on_error(self):
        sender = MagicMock()
        sender.schedule.time = MagicMock(return_value = (5, 10, 15))
        request = Request(sender, 0, "foo_operation", 1)

        recipient = MagicMock()

        request.send_to(recipient)
        request.reply_error()

        with self.assertRaises(AssertionError):
            request.response_time

