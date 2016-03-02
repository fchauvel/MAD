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
    An entry in the log
    """

    def __init__(self, time, context, message):
        self.time = time
        self.context = context
        self.message = message

    def __repr__(self):
        return "%4d %-20s %-40s" % (self.time, self.context, self.message)


class Log:
    """
    The history of message logged recorded during a simulation
    """

    def __init__(self):
        self.entries = []

    def __repr__(self):
        return "\n".join([str(each_entry) for each_entry in self.entries])

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        for each_entry in self.entries:
            yield each_entry

    @property
    def is_empty(self):
        return len(self) == 0

    @property
    def size(self):
        return len(self)

    def record(self, time, context, message):
        self.entries.append(Event(time, context, message))