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

from random import choice


class Agent:
    """
    Represent an agent that can be simulated such as a turtle, a person or a bathtube.
    """

    def __init__(self):
        self._schedule = []
        self._clock = Clock()

    @property
    def next_events(self):
        """
        Return the of this agents, that will be triggered next. There may be several event scheduled at the same time.
        """
        if len(self._schedule) == 0:
            return []
        earliest = min(self._schedule, key=lambda event: event.time)
        return [any_event for any_event in self._schedule if any_event.is_earlier_than(earliest)]

    def schedule(self, action, at):
        """
        Schedule the given action at the given time
        """
        self._schedule.append(Event(self, action, self._clock.time + at))

    def _discard(self, event):
        self._schedule.remove(event)

    @property
    def _has_more_events(self):
        return len(self.next_events) > 0

    def setup(self):
        pass

    def _run_until(self, time):
        self.setup()
        while self._has_more_events \
                and not self._clock.passed(time):
            next_event = choice(self.next_events)
            next_event.trigger()


class Event:
    """
    Represent the planned triggering of an action
    """

    def __init__(self, context, action, time):
        self._context = context
        self._action = action
        self._time = time

    @property
    def action(self):
        return self._action

    @property
    def time(self):
        return self._time

    def is_earlier_than(self, other_event):
        return self.time <= other_event.time

    def trigger(self):
        self._context._clock.advance_to(self._time)
        self._action.fire()
        self._context._discard(self)


class Action:
    """
    Represent an action performed by an agent.
    """

    def fire(self):
        pass


class Clock:
    """
    Represent a clock, that monitor the current time (i.e., the time where the last event was triggered)
    """

    def __init__(self, initial_time = 0):
        self._time = initial_time

    @property
    def time(self):
        return self._time

    def passed(self, deadline):
        return self._time > deadline

    def advance_to(self, new_time):
        assert new_time >= self._time, "Time is moving backward (now: %d ; then: %d)" % (self._time, new_time)
        self._time = new_time

