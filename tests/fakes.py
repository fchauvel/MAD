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

from mad.log import Log, Event
from mad.storage import DataStorage
from mad.monitoring import CSVReport


class InMemoryDataStorage(DataStorage):

    def __init__(self, model):
        self._log = InMemoryLog()
        self._model = model
        self._opened_reports = {}

    @property
    def log(self):
        return self._log

    def model(self):
        return self._model

    def report_for(self, entity, format):
        if entity not in self._opened_reports:
            self._opened_reports[entity] = CSVReport(StringIO(), format)
        return self._opened_reports[entity]


class InMemoryFileSystem:

    def __init__(self):
        self.opened_files = {}

    def define(self, location, content):
        self.opened_files[location] = StringIO(content)

    def open_input_stream(self, location):
        if location not in self.opened_files:
            raise FileNotFoundError(location)
        return self.opened_files[location]

    def open_output_stream(self, location):
        if location not in self.opened_files:
            self.opened_files[location] = StringIO()
        return self.opened_files[location]

    def has_file(self, file):
        for any_location in self.opened_files:
            if any_location.endswith(file):
                return True
        return False


class InMemoryLog(Log):
    """
    Hold the history of events in a list for later processing
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