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


class Event:
    """
    Hold a action (i.e., a callable object) and the time at which this action shall be triggered
    """

    def __init__(self, time, action):
        if not isinstance(time, int):
            raise ValueError("Time must be an integer value (found '%s')." % type(time))
        self.time = time

        if not callable(action):
            raise ValueError("Only 'callable' objects can be scheduled (found '%s')." % (type(action)))
        self.action = action

    def __repr__(self):
        return "Event(%d, %s)" % (self.time, str(self.action))

    def trigger(self):
        self.action()

    def is_scheduled_after(self, time):
        return self.time > time

    def is_scheduled_before(self, time):
        return not self.is_scheduled_after(time)


class EventPool:
    """
    An event pool that store events, and expose then the increasing order of their due time
    """

    def __init__(self):
        self.events = []

    def put(self, event):
        self.events.append(event)

    def next_event(self):
        assert not self.is_empty, "No event is scheduled"
        return min(self.events, key=lambda event: event.time)

    def discard(self, event):
        self.events.remove(event)

    @property
    def is_empty(self):
        return len(self.events) == 0


class Clock:
    """
    A simple clock, which can only advance
    """

    def __init__(self, initial_time):
        self._time = initial_time

    @property
    def time(self):
        return self._time

    def advance_to(self, event):
        assert self.time <= event.time, "Time is moving backward (now %d, next %d)" % (self.time, event.time)
        self._time = event.time

    def is_over(self, limit):
        return self.time > limit

    def has_passed(self, event):
        return event.is_scheduled_before(self._time)


class Scheduler:
    """
    Maintain a ordered list of events, which are executed according to their due date.
    """

    def __init__(self, initial_time=0):
        self.schedule = EventPool()
        self.clock = Clock(initial_time)

    @property
    def time_now(self):
        return self.clock.time

    def at(self, time, action):
        event = Event(time, action)
        if event.is_scheduled_before(self.clock.time):
            raise ValueError("Cannot schedule in the past (now is %d but found %d)" % (self.clock.time, time))
        self.schedule.put(event)

    def after(self, delay, action):
        self.schedule.put(Event(self.time_now + delay, action))

    def every(self, period, action):
        def recurrent_action():
            action()
            self.after(period, recurrent_action)
        self.after(period, recurrent_action)

    def simulate_until(self, end, display=None):
        while not self.schedule.is_empty:
            event = self.schedule.next_event()
            if event.is_scheduled_after(end):
                break
            self.clock.advance_to(event)
            if display: display.update(self.time_now, end)
            event.trigger()
            self.schedule.discard(event)



