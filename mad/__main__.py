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

from mad import __version__
from mad.sensitivity import SensitivityAnalysis, RejectionRate, ResponseTime, ClientRequestRate

VERSION = "MAD v%s" % __version__
COPYRIGHT = "Copyright (C) 2015 Franck Chauvel"

DISCLAIMER = "This program comes with ABSOLUTELY NO WARRANTY\n" \
             "This is free software, and you are welcome to redistribute it\n" \
             "under certain conditions."


print(VERSION)
print(COPYRIGHT)
print()
print(DISCLAIMER)
print()

print("Sensitivity Analysis:")
analysis = SensitivityAnalysis()
analysis.run_count = 100
analysis.parameters = [ RejectionRate(), ResponseTime(), ClientRequestRate() ]
analysis.run()

print("That's all folks.")