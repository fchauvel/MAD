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


class Environment:
    """
    Hold bindings that associate a symbol to an object during the simulation
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}

    def define(self, symbol, value):
        self.bindings[symbol] = value

    def look_up(self, symbol):
        if symbol in self.bindings:
            return self.bindings[symbol]
        elif self.is_local:
            return self.parent.look_up(symbol)
        else:
            return None

    @property
    def is_global(self):
        return self.parent is None

    @property
    def is_local(self):
        return not self.is_global

    def create_local_environment(self):
        return Environment(self)