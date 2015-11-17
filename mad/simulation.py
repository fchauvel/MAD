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

from random import shuffle
from io import StringIO


class Agent:
    """
    Represent an agent that can be simulated such as a turtle, a person or a bathtube.
    """

    def __init__(self, identifier):
        self._identifier = identifier
        self._schedule = []
        self._clock = Clock()
        self._container = None
        self._recorders = RecorderBroker()
        self._parameters = []

    @property
    def is_contained(self):
        return self.container is not None

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, new_container):
        self._container = new_container

    @property
    def identifier(self):
        return self._identifier

    @property
    def clock(self):
        return self._clock

    @clock.setter
    def clock(self, new_clock):
        self._clock = new_clock

    @property
    def current_time(self):
        return self._clock.time

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, new_parameters):
        self._parameters = new_parameters

    @property
    def next_events(self):
        """
        Return the events that shall be triggered next, that is to say the earliest events in the schedule of this agent.
        Note that there may be several event scheduled at the same time.
        """
        return self._earliest_of(self._schedule)

    def _earliest_of(self, events):
        if len(events) == 0: return []
        earliest = min(events, key=lambda event: event.time)
        return [any_event for any_event in events if any_event.is_earlier_than(earliest)]

    def schedule_in(self, action, delay):
        """
        Schedule the given action at the given time
        """
        self._schedule.append(Event(self, action, self._clock.time + delay))

    def _discard(self, event):
        self._schedule.remove(event)

    @property
    def _has_more_events(self):
        return len(self.next_events) > 0

    def setup(self):
       pass

    def teardown(self):
        self._recorders[self.identifier].close()

    def on_start(self):
        pass

    def run_until(self, time):
        self.clock = Clock()
        self.on_start()
        self.record_state()
        while self._has_more_events and not self._clock.has_passed(time):
            events = self.next_events
            shuffle(events)
            for each_event in events:
                each_event.trigger()
            self.record_state()

    def record_state(self):
        pass

    def record(self, entries):
        all_entries = self._parameters + [("time", "%d", self._clock.time)] + entries
        self._recorders[self.identifier].record(all_entries)

    @property
    def recorders(self):
        return self._recorders

    @recorders.setter
    def recorders(self, new_recorders):
        self._recorders = new_recorders

    def log(self, message):
        """
        Log a given message on the standard output
        """
        print("t=%04d - %s" % (self._clock.time, message))

    def locate(self, identifier):
        """
        Locate a component in the hierarchy
        """
        if self.is_named(identifier):
            return self
        else:
            if self.is_contained:
                return self._container.locate(identifier)
            raise ValueError("Could not locate agent '%s'" % identifier)

    def is_named(self, identifier):
        return self.identifier == identifier


class CompositeAgent(Agent):
    """
    Represent a composite agents, i.e., agents made out of other agents
    """
    def __init__(self, identifier, *agents):
        super().__init__(identifier)
        for each_agent in agents:
            if not isinstance(each_agent, Agent):
                raise ValueError("Only 'agent' object are expected (found '%s')", type(each_agent))
            else:
                each_agent.container = self
        self._agents = agents

    @property
    def agents(self):
        return self._agents

    @Agent.parameters.setter
    def parameters(self, new_parameters):
        Agent.parameters.fset(self, new_parameters)
        for each_agent in self.agents:
            each_agent.parameters = new_parameters

    @Agent.recorders.setter
    def recorders(self, new_recorders):
        Agent.recorders.fset(self, new_recorders)
        for each_agent in self.agents:
            each_agent.recorders = new_recorders

    def on_start(self):
        self.on_start_composite()
        for each_agent in self.agents:
            each_agent.on_start()

    def on_start_composite(self):
        pass

    def setup(self):
        super().setup()
        for each_agent in self.agents:
            each_agent.setup()

    def teardown(self):
        for each_agent in self.agents:
            each_agent.teardown()

    @Agent.clock.setter
    def clock(self, new_clock):
        self._clock = new_clock
        for each_agent in self.agents:
            each_agent.clock = new_clock

    @property
    def next_events(self):
        return self._earliest_of(self._aggregate())

    def _aggregate(self):
        result = []
        for each_agent in self.agents:
            result.extend(each_agent.next_events)
        return result

    def locate(self, identifier):
        for any_agent in self.agents:
            if any_agent.is_named(identifier):
                return any_agent
        return super().locate(identifier)

    def record_state(self):
        self.record_composite_state()
        for each_agent in self.agents:
            each_agent.record_state()

    def record_composite_state(self):
        pass


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

    def has_passed(self, deadline):
        return self._time >= deadline

    def advance_to(self, new_time):
        assert new_time >= self._time, "Time is moving backward (now: %d ; then: %d)" % (self._time, new_time)
        self._time = new_time


class Recorder:
    """
    Record the state of an agent
    """

    def __init__(self, id, output=StringIO()):
        self._entry_count = 0
        self._output = output

    def record(self, entry):
        if self._is_first_record():
            self._write_header(entry)
        self._write_record(entry)

    def _is_first_record(self):
        return self._entry_count == 0

    def _write_header(self, entries):
        keys = [key for (key, _, _) in entries ]
        self._write(", ".join(keys))
        self._new_line()

    def _write_record(self, entries):
        format = ", ".join([format for (_, format, _) in entries])
        self._write(format % tuple([value for (_, _, value) in entries]))
        self._new_line()
        self._entry_count += 1

    def _new_line(self):
        self._write("\n")

    def _write(self, text):
        self._output.write(text)

    def close(self):
        self._output.close()


class RecorderBroker:
    """
    Provide access to a set of recorders by keys. It creates a new recorder, when it meets an unknown key
    """
    def default_factory(prefix, name):
        return Recorder(name, RecorderBroker._file_for(prefix, name))

    def _file_for(prefix, name):
        log_file = RecorderBroker._escape(prefix) + "_log_" + RecorderBroker._escape(name) + ".csv"
        return open(log_file, "w", encoding="utf-8")

    def _escape(text):
        return text.replace(" ", "_")

    def __init__(self, prefix="", factory=default_factory):
        self._prefix = prefix
        self._factory = factory
        self._recorders = {}

    def __getitem__(self, key):
        if key in self._recorders.keys():
            return self._recorders[key]
        else:
            recorder = self._factory(self._prefix, key)
            self._recorders[key] = recorder
            return recorder

    def close_all(self):
        for (_, each_recorder) in self._recorders.items():
            each_recorder.close()