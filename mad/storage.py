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



class DataStorage:

    def __init__(self, parser, log, factory):
        self.parser = parser
        self.log = log
        self.report_factory = factory

    def model(self):
        return self.parser.parse()

    def log(self):
        return self.log

    def report_for(self, name, format):
        return self.report_factory(name, format)

