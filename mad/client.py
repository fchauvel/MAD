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


class Request:
    """
    A request send by a 'client' to a 'server'
    """

    def __init__(self, sender):
        self._sender = sender

    def reply(self):
        self._sender.accept_response()


class Send(Action):
    """
    Capture the client sending a single request, and then scheduling the departure of the next request
    """

    def __init__(self, sender):
        self._sender = sender

    def fire(self):
        self._sender.server.process(Request(self._sender))
        self._sender.prepare_next_request()


class Client(Agent):
    """
    A 'client' emits requests at a fixed frequency
    """

    def __init__(self, identifier, request_rate):
        super().__init__(identifier)
        self._request_rate = request_rate
        self._server = None

    @property
    def inter_request_period(self):
        return int(1/self._request_rate)

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, new_server):
        self._server = new_server

    def setup(self):
        self.prepare_next_request()

    def prepare_next_request(self):
        self.schedule_in(Send(self), delay=self.inter_request_period)

    def accept_response(self):
        self.log("response received")


