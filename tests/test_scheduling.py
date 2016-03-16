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

from mad.scheduling import Scheduler


class DummyAction:

    def __init__(self, schedule):
        self.schedule = schedule
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append(self.schedule.time_now)

    def was_called_once_at(self, time):
        return len(self.calls) == 1 and self.calls[0] == time

    def was_called_at(self, times):
        return self.calls == times


class SchedulerTest(TestCase):
    """
    Specification of the scheduler component
    """

    def test_scheduling_an_action_at_a_given_time(self):
        schedule = Scheduler()
        action = DummyAction(schedule)
        schedule.at(10, action)

        schedule.simulate_until(20)

        self.assertEqual(10, schedule.time_now)
        self.verify_calls([10], action)

    def test_scheduling_action_in_the_past_is_forbidden(self):
        schedule = Scheduler(20)
        action = DummyAction(schedule)

        with self.assertRaises(ValueError):
            schedule.at(10, action)

    def test_scheduling_an_action_after_a_delay(self):
        schedule = Scheduler()
        action = DummyAction(schedule)
        schedule.after(5, action)

        schedule.simulate_until(20)

        self.assertEqual(5, schedule.time_now)
        self.verify_calls([5], action)

    def test_scheduling_an_object_is_forbidden(self):
        schedule = Scheduler()
        action = "This is not a callable!"
        with self.assertRaises(ValueError):
            schedule.at(10, action)

    def test_scheduling_twice_an_action_at_a_given_time(self):
        schedule = Scheduler()
        action = DummyAction(schedule)
        schedule.at(5, action)
        schedule.at(5, action)

        schedule.simulate_until(20)

        self.assertLessEqual(5, schedule.time_now)
        self.verify_calls([5, 5], action)

    def test_scheduling_an_action_with_a_given_period(self):
        schedule = Scheduler()
        action = DummyAction(schedule)
        schedule.every(5, action)

        schedule.simulate_until(20)

        self.assertLessEqual(20, schedule.time_now)
        self.verify_calls([5, 10, 15, 20], action)

    def test_simulation_orders_events(self):
        schedule = Scheduler()
        action = DummyAction(schedule)
        schedule.at(10, action)
        schedule.at(5, action)

        schedule.simulate_until(20)

        self.verify_calls([5, 10], action)

    def test_scheduling_at_a_non_integer_time(self):
        schedule = Scheduler()
        action = DummyAction(schedule)

        with self.assertRaises(ValueError):
            schedule.at("now", action)

    def verify_calls(self, expectation, action):
        self.assertTrue(action.was_called_at(expectation), "Action called on %s" % str(action.calls))




if __name__ == "__main__":
    from unittest import main
    main()

