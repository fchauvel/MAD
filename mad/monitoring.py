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


class CSVReport:
    """
    Format monitored data as CSV entries and push them in the designated
    output stream.
    """

    def __init__(self, output, fields_format):
        self.output = output
        self.formats = fields_format
        self._print_headers()

    def _print_headers(self):
        field_names = [ each_key.replace("_", " ") for (each_key, _) in self.formats ]
        self.output.write(", ".join(field_names))
        self.output.write("\n")

    def __call__(self, *args, **kwargs):
        texts = []
        for (field_name, format) in self.formats:
            if field_name in kwargs:
                texts.append(format % kwargs[field_name])
            else:
                texts.append("??")
        self.output.write(", ".join(texts))
        self.output.write("\n")

