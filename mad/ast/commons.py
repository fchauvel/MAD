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

class Expression:
    """
    Abstract Expression class
    """

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        assert isinstance(other, Expression), "Can only sequence expressions (found '%s')" % type(other)
        if isinstance(other, Sequence):
            content = [self] + other.body
        else:
            content = [self, other]
        return Sequence(*content)

    def accept(self, evaluation):
        raise NotImplementedError("Expression::accept is abstract!")


class Sequence(Expression):
    """
    A sequence of actions (i.e., invocation or think)
    """

    def __init__(self, *args, **kwargs):
        self.body = list(args)

    @property
    def first_expression(self):
        return self.body[0]

    @property
    def rest(self):
        if len(self.body) > 2:
            return Sequence(*self.body[1:])
        else:
            return self.body[1]

    def accept(self, evaluation):
        return evaluation.of_sequence(self)

    def __repr__(self):
        body = [str(each_expression) for each_expression in self.body]
        return "Sequence(%s)" % ", ".join(body)

    def __add__(self, other):
        assert isinstance(other, Expression), "Can only sequence expressions (found '%s')" % type(other)
        if isinstance(other, Sequence):
            content = self.body + other.body
        else:
            content = self.body + [other]
        return Sequence(*content)

