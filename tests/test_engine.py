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
from mock import MagicMock

from mad.engine import Agent, Action


class DummyAgent(Agent):

    def __init__(self):
        super().__init__()
        self._counter = 0
        self._action = DummyAction(self)

    def setup(self):
        self.schedule(self._action, 10);

    def called_once(self):
        self._counter += 1


class DummyAction(Action):

    def __init__(self, subject):
        super().__init__()
        self._subject = subject

    def fire(self):
        self._subject.called_once()
        self._subject.schedule(self, 10)


class EngineTest(TestCase):

    def test_that_scheduled_action_are_visible(self):
        agent = DummyAgent()
        action = MagicMock(Action)

        agent.schedule(action, at=10)
        agent.schedule(action, at=20)
        agent.schedule(action, at=10)

        self.assertTrue(len(agent.next_events) == 2)

    def test_that_events_are_triggered_and_then_discarded(self):
        agent = DummyAgent()
        action = MagicMock(Action)
        agent.schedule(action, at=15)

        agent.next_events[0].trigger()

        action.fire.called_once()
        self.assertTrue(len(agent.next_events) == 0)

    def test_running_dummy_simulation(self):
        agent = DummyAgent()

        agent._run_until(50)

        self.assertEqual(6, agent._counter)


if __name__ == "__main__":
    main()