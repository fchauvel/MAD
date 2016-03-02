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

from mad.des2.scheduling import Scheduler
from mad.des2.log import Log


class Symbols:
    SELF = "!self"
    REQUEST = "!request"
    SERVICE = "!service"


class Environment:
    """
    Hold bindings that associate a symbol to an object during the simulation
    """

    def __init__(self):
        self.bindings = {}

    def schedule(self):
        raise NotImplementedError("Method 'Environment::schedule' is abstract!")

    def log(self):
        raise NotImplementedError("Method 'Environment::log' is abstract")

    def define(self, symbol, value):
        self.bindings[symbol] = value

    def define_each(self, symbols, values):
        if len(symbols) != len(values):
            raise ValueError("Inconsistent symbols and values (found symbols %s, values %s)" % (symbols, values))

        for (symbol, value) in zip(symbols, values):
            self.define(symbol, value)

    def look_up(self, symbol):
        return self.bindings.get(symbol, None)

    def create_local_environment(self):
        return LocalEnvironment(self)

    def next_request_id(self):
        raise NotImplementedError("Environment::next_request_id is abstract!")


class GlobalEnvironment(Environment):

    def __init__(self, scheduler = None):
        super().__init__()
        self._scheduler = scheduler or Scheduler()
        self._log = Log()
        self._next_request_id = 1

    def schedule(self):
        return self._scheduler

    def log(self):
        return self._log

    def next_request_id(self):
        id = self._next_request_id
        self._next_request_id += 1
        return id


class LocalEnvironment(Environment):

    def __init__(self, parent):
        super().__init__()
        assert isinstance(parent, Environment), "Environment must be enclosed within other environments (found %s)" % type(parent)
        self.parent = parent

    def look_up(self, symbol):
        result = super().look_up(symbol)
        if result is None:
            result = self.parent.look_up(symbol)
        return result

    def schedule(self):
        return self.parent.schedule()

    def log(self):
        return self.parent.log()

    def next_request_id(self):
        return self.parent.next_request_id()