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

class Environment:
    """
    Hold bindings that associate a symbol to an object during the simulation
    """

    def __init__(self, scheduler=Scheduler()):
        self.bindings = {}
        self.scheduler = scheduler

    @property
    def schedule(self):
        return self.scheduler

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

    @property
    def schedule(self):
        return super().schedule
