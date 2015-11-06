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

from mad.engine import Agent, Action
from mad.client import Request
from mad.throttling import StaticThrottling


class ServiceStub(Agent):
    """
    A service stub, on which one can adjust the response time and the rejection rate
    """

    def __init__(self, response_time=10, rejection_rate=0.1):
        super().__init__("Service Stub")
        self._response_time = response_time
        self._throttling = StaticThrottling(rejection_rate)

    @property
    def response_time(self):
        return self._response_time

    @response_time.setter
    def response_time(self, new_response_time):
        self._response_time = new_response_time

    @property
    def rejection_rate(self):
        return self.rejection_rate

    @rejection_rate.setter
    def rejection_rate(self, new_rejection_rate):
        self._throttling = StaticThrottling(new_rejection_rate)

    def process(self, request):
        if self._throttling.accepts(request):
            self.schedule_in(Reply(self, request), self._response_time)
        else:
            request.reject()


class Reply(Action):
    """
    Reply to the given request
    """

    def __init__(self, subject, request):
        self._subject = subject
        self._request = request

    def fire(self):
        self._request.reply()


class ClientStub(Agent):
    """
    A client stub that send request at a fixed rate, regardless of whether they are rejected or successful
    """

    def __init__(self, emission_rate=0.5):
        super().__init__("client stub")
        self._emission_rate = emission_rate
        self._server = None

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, new_server):
        self._server = new_server

    def on_start(self):
        self.prepare_next_request()

    def prepare_next_request(self):
        self.schedule_in(SendRequest(self), self.inter_request_time)

    @property
    def inter_request_time(self):
        return round(1/self._emission_rate)

    def send_request(self):
        Request(self).send_to(self.server)
        self.prepare_next_request()

    def on_completion_of(self, request):
        pass

    def on_rejection_of(self, request):
        pass


class SendRequest(Action):
    """
    Trigger the sending of a single request
    """

    def __init__(self, subject):
        super().__init__()
        self._subject = subject

    def fire(self):
        self._subject.send_request()