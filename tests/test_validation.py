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

from mad.validation.issues import *
from mad.validation.engine import Validator, InvalidModel


class ValidatorTests(TestCase):

    def test_all_errors(self):
        for each_case in self.all_erroneous_cases():
            self._do_test(**each_case)

    def _do_test(self, expression, expected_errors):
        try:
            validation = Validator()
            validation.validate(expression)
            if not validation.raised_warnings():
                self.fail("Expecting issue detected for expression %s" % str(expression))
            else:
                self._verify_issues(expression, validation.errors, expected_errors)

        except InvalidModel:
            self._verify_issues(expression, validation.errors, expected_errors)

    def _verify_issues(self, expression, actual, expected):
            for each_expected_error in expected:
                self.assertTrue(each_expected_error in actual,
                                "Expression '%s'\n"
                                "should raise %s\n"
                                "but found %s" % (str(expression), expected, actual))

    def all_erroneous_cases(self):
        return [
            self.unknown_service(),
            self.empty_service(),
            self.unknown_operation(),
            self.duplicate_service(),
            self.duplicate_operation(),
            self.never_invoked_operation(),
        ]

    def unknown_operation(self):
        return {"expression":
            Sequence(
                DefineService("DB", DefineOperation("Insert", Think(5))),
                DefineClientStub("Erroneous", 2, Trigger("DB", "Select"))),
            "expected_errors":
                [UnknownOperation("DB", "Select")]}

    def duplicate_operation(self):
        return {"expression":
                    DefineService("DB", Sequence(
                        DefineOperation("Insert", Think(5)),
                        DefineOperation("Insert", Think(5)))
                                  ),
                "expected_errors":
                    [DuplicateOperation("DB", "Insert")]}

    def duplicate_service(self):
        return {"expression":
            Sequence(
                DefineService("DB", DefineOperation("Insert", Think(5))),
                DefineService("DB", DefineOperation("Select", Think(5)))),
            "expected_errors":
                [DuplicateIdentifier("DB")]}

    def empty_service(self):
        return {"expression":
                    DefineService("DB", Sequence()),
                "expected_errors":
                    [EmptyService("DB")]}

    def never_invoked_operation(self):
        return {"expression":
                    DefineService("DB", Sequence(DefineOperation("Insert", Think(5)))),
                "expected_errors":
                    [NeverInvokedOperation("DB", "Insert")]}

    def unknown_service(self):
        return {"expression":
                    DefineClientStub("Browser", 2, Trigger("DB", "Select")),
                "expected_errors":
                    [UnknownService("DB")]}


if __name__ == "__main__":
    import unittest.main as main
    main()