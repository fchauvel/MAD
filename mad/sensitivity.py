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
from mad.throttling import StaticThrottling


class ServiceStub(Agent):
    """
    A service stub, on which one can adjust the response time and the rejection rate
    """

    def __init__(self, response_time=10, rejection_rate=0.1):
        super().__init__("Service Stub")
        self._response_time = response_time
        self._throttling = StaticThrottling(rejection_rate)

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