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

from sys import argv, stdout

from mad.des2.parsing import Parser

from mad.datasource import Mad, InFilesDataSource
from mad.ui import CommandLineInterface, Display, Arguments


source = InFilesDataSource()
mad = Mad(Parser(source), source)
cli = CommandLineInterface(Display(stdout), mad)

project = Arguments(argv[1:]).as_project
cli.simulate(project)

