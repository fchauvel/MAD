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

from unittest import TestCase


from mad.ast.definitions import DefineClientStub, DefineOperation, DefineService
from mad.ast.actions import Trigger, Think
from mad.ast.commons import Sequence

from mad.validation import Validator, UnknownService, UnknownOperation


class ValidatorTests(TestCase):

    def test_all_errors(self):
        for each_case in self.all_erroneous_cases():
            self._do_test(*each_case)

    def _do_test(self, expression, expected_errors):
        validation = Validator(expression)
        for each_expected_error in expected_errors:
            self.assertTrue(each_expected_error in validation.errors)

    def all_erroneous_cases(self):
        return [
            (DefineClientStub("Erroneous", 2, Trigger("DB", "Select")),
             [UnknownService("DB")]),

             (Sequence(
                DefineService(
                    "DB",
                    Sequence(DefineOperation("Insert", Think(5)))),
                DefineClientStub("Erroneous", 2, Trigger("DB", "Select"))),
              [UnknownOperation("DB", "Select")])
        ]


if __name__ == "__main__":
    import unittest.main as main
    main()