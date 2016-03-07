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

from mad.des2.simulation import Simulation


class Interpreter:

    def evaluate(self, expression):
        simulation = Simulation()
        simulation.evaluate(expression)
        return simulation


class FileSource:

    def __init__(self, model):
        pass


class Repository:

    def __init__(self, parser, interpreter):
        self.parser = parser
        self.interpreter = interpreter

    def load(self, model):
        expression = self.parser.parse(FileSource(model))
        return self.interpreter.evaluate(expression)
