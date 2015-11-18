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


from io import StringIO
from unittest import TestCase, main
from mock import MagicMock

from mad.simulation import Agent, CompositeAgent, Action, Recorder, RecorderBroker


class DummyAgent(Agent):

    def __init__(self, period = 10, identifier = "Dummy Agent"):
        super().__init__(identifier)
        self.period = period
        self._counter = 0
        self._action = DummyAction(self)

    def on_start(self):
        self.schedule_in(self._action, self.period);

    def called_once(self):
        #self.log("dummy action (P=%d)" % self.period)
        self._counter += 1


class DummyAction(Action):

    def __init__(self, subject):
        super().__init__()
        self._subject = subject

    def fire(self):
        self._subject.called_once()
        self._subject.schedule_in(self, self._subject.period)


class EngineTest(TestCase):

    def test_qualified_identifier(self):
        agent = DummyAgent(identifier="bob")
        simulation = CompositeAgent("simulation", agent)

        self.assertEqual("simulation/bob", agent.qualified_identifier)

    def test_trace_is_none_by_default(self):
        agent = DummyAgent()
        self.assertIsNone(agent.trace)

    def test_trace_can_be_set(self):
        agent = DummyAgent()
        output = StringIO()
        agent.trace = output
        self.assertIs(output, agent.trace)

    def test_composite_set_trace_recursively(self):
        agent = DummyAgent()
        composite = CompositeAgent("container", agent)
        output = StringIO()
        composite.trace = output
        self.assertIs(output, agent.trace)

    def test_log_are_written_on_the_debug_trace(self):
        agent = DummyAgent()
        output = StringIO()
        agent.trace = output
        agent.log("test message")
        self.assertTrue("test message" in output.getvalue())

    def test_that_scheduled_action_are_visible(self):
        agent = DummyAgent()
        action = MagicMock(Action)

        agent.schedule_in(action, delay=10)
        agent.schedule_in(action, delay=20)
        agent.schedule_in(action, delay=10)

        self.assertTrue(len(agent.next_events) == 2)

    def test_that_events_are_triggered_and_then_discarded(self):
        agent = DummyAgent()
        action = MagicMock(Action)
        agent.schedule_in(action, delay=15)

        agent.next_events[0].trigger()

        action.fire.called_once()
        self.assertTrue(len(agent.next_events) == 0)

    def test_running_dummy_simulation(self):
        agent = DummyAgent()

        agent.run_until(50)

        self.assertEqual(5, agent._counter)

    def test_composite_agent(self):
        agent1 = DummyAgent(10)
        agent2 = DummyAgent(20)
        simulation = CompositeAgent("simulation", agent1, agent2)

        simulation.run_until(time=50)

        self.assertEqual(5, agent1._counter)
        self.assertEqual(2, agent2._counter)

    def test_localisation_of_components_in_the_hierarchy(self):
        agent1 = DummyAgent(10, "A1")
        agent2 = DummyAgent(20, "A2")
        level1 = CompositeAgent("level1", agent1, agent2)
        agent3 = DummyAgent(10, "A3")
        level2 = CompositeAgent("level2", level1, agent3)
        self.assertIs(agent3, agent1.locate("A3"))

    def test_agents_can_have_parameters(self):
        agent = DummyAgent(10, "A1")
        simulation = CompositeAgent("composite", agent)

        simulation.parameters = [("name", "%d", 23)]

        self.assertEqual("name", agent.parameters[0][0])


class RecorderTest(TestCase):

    def test_agent_state_is_recorded(self):
        agent = DummyAgent(10, "A1")
        agent.record_state = MagicMock(Recorder)

        agent.run_until(100)

        self.assertEqual(11, agent.record_state.call_count)

    def test_all_agent_state_are_recorded(self):
        agent = DummyAgent(10, "A1")
        agent.record_state = MagicMock(Recorder)
        simulation = CompositeAgent("composite", agent)

        simulation.run_until(100)

        self.assertEqual(11, agent.record_state.call_count)

    def test_recording_state(self):
        output = StringIO()
        recorder = Recorder("test", output)
        recorder.record([
            ("counter", "%d", 1),
            ("value", "%.1f", 50.4)
        ])
        recorder.record([
            ("counter", "%d", 2),
            ("value", "%.1f", 54.3)
        ])
        expected = ("counter, value\n"
                    "1, 50.4\n"
                    "2, 54.3\n")
        self.assertEqual(expected, output.getvalue())

    def test_recording(self):
        collector = StringIO()
        factory = MagicMock(side_effect=[Recorder("A", collector)])
        recording = RecorderBroker("", factory)
        recording["A"].record([("value", "%d", 1), ("rate", "%.1f", 0.2)])
        recording["A"].record([("value", "%d", 2), ("rate", "%.1f", 0.4)])

        expectation = ("value, rate\n"
                      "1, 0.2\n"
                      "2, 0.4\n")

        self.assertEqual(expectation, collector.getvalue())






if __name__ == "__main__":
    main()