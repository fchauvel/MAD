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


class ReportFactory:
    """
    Factory that produce reports for both service and clients. Each
    report is associated with a name, so that it never recreated.
    """

    def __init__(self):
        self._registry = {}

    def report_for_service(self, name):
        return self._fetch_or_create(name, self._make_report_for_service)

    def report_for_client(self, name):
        return self._fetch_or_create(name, self._make_report_for_client)

    def _fetch_or_create(self, name, factory):
        if name not in self._registry:
            report = factory(name)
            self._registry[name] = report
            return report
        else:
            return self._registry[name]

    def _make_report_for_service(self, name):
        raise NotImplementedError("ReportFactory::_make_report_for_service is abstract")

    def _make_report_for_client(self, client_name):
        raise NotImplementedError("ReportFactory::_make_report_for_client is abstract")


class CSVReportFactory(ReportFactory):

    def __init__(self, project, repository):
        super().__init__()
        self.project = project
        self.repository = repository

    def _make_report_for_service(self, service):
        return self._make_report(  service,
                            [("time", "%5d"),
                             ("queue_length", "%5d"),
                             ("utilisation", "%6.2f"),
                             ("worker_count", "%5d"),
                             ("rejection_count", "%5d")])

    def _make_report_for_client(self, client):
        # TODO: Update this definition
        return self._make_report(  client,
                            [("time", "%5d"),
                            ("queue_length", "%5d")])

    def _make_report(self, name, format):
        resource = self.project.report_for(name)
        output = self.repository.open_stream_to(resource)
        return CSVReport(output, format)


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

