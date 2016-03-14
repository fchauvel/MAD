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

from re import search
from datetime import datetime
from os import makedirs
from os.path import exists, dirname
from io import StringIO

from mad.des2.simulation import Simulation
from mad.des2.log import FileLog
from mad.des2.monitoring import CSVReportFactory


class Settings:
    TRACE_FILE = "trace.log"
    REPORT_NAME = "%s.log"

    @staticmethod
    def new_identifier():
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class Project:

    @staticmethod
    def from_arguments(arguments):
        if len(arguments) != 2:
            raise ValueError("Missing arguments (expected [my-file.mad] [simulation-length], but found '%s')" % arguments)
        file_name = Project._extract_file_name(arguments)
        length = Project._extract_length(arguments)
        return Project(file_name, length)

    @staticmethod
    def _extract_file_name(arguments):
        result = arguments[0]
        if not isinstance(result, str):
            raise ValueError("Expecting 'MAD file' as Argument 1, but found '%s'" % arguments[0])
        return result

    @staticmethod
    def _extract_length(arguments):
        try:
            return int(arguments[1])
        except ValueError:
            raise ValueError("Expecting simulation length as Argument 2, but found '%s'" % arguments[1])

    def __init__(self, root_mad_file, limit):
        self.file_name = root_mad_file
        self.limit = limit

    @property
    def root_file(self):
        return self.file_name

    @property
    def name(self):
        match = search(r"([^\\/]+)\.(\w+)$", self.file_name)
        if match:
            return match.group(1)
        else:
            return self.file_name

    @property
    def output_directory(self):
        return "%s_%s" % (self.name, Settings.new_identifier())

    @property
    def log_file(self):
        return "%s/%s" % (self.output_directory, Settings.TRACE_FILE)

    def report_for(self, entity_name):
        report_name = Settings.REPORT_NAME % entity_name
        return "%s/%s" % (self.output_directory, report_name)


class Mad:
    """
    Represent the simulation engine. It access the repository, parse the model and
    build the simulation.
    """

    def __init__(self, parser, output):
        self.parser = parser
        self.output = output

    def load(self, project):
        logger = self._create_logger(project.log_file)
        simulation = Simulation(logger, CSVReportFactory(project, self.output))
        expression = self.parser.parse(project.root_file)
        simulation.evaluate(expression)
        return simulation

    def _create_logger(self, file_name):
        return FileLog(self.output.open_stream_to(file_name), "%5d %-20s %-s\n")


class Repository:
    """
    Unified interface for opening resources, identified by name
    """

    @staticmethod
    def open_stream_to(path):
        raise NotImplementedError("Method Repository::open_stream_to is abstract")

    @staticmethod
    def read(model):
        raise NotImplementedError("Method Repository::read is abstract")


class FileSource(Repository):

    @staticmethod
    def open_stream_to(path):
        if not exists(path):
            makedirs(dirname(path), exist_ok=True)
        return open(path, "w+")

    @staticmethod
    def read(model):
        with open(model) as file:
            return file.read()


class InMemoryDataSource(Repository):

    def __init__(self, streams = {}):
        self.streams = streams

    def open_stream_to(self, path):
        if path not in self.streams:
            self.streams[path] = StringIO()
        return self.streams[path]

    def read(self, model):
        if model not in self.streams:
            raise RuntimeError("Unknown resource '%s' (Candidates are %s)" % (model, str(self.streams.keys())))
        else:
            return self.streams[model]

