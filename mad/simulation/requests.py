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


class Request:
    QUERY = 0
    TRIGGER = 1

    TRANSMISSION_DELAY = 1

    PENDING = 0
    OK = 1
    ERROR = 2
    ACCEPTED = 3
    REJECTED = 4

    def __init__(self, sender, kind, operation, priority, on_accept=lambda:None, on_reject=lambda:None, on_success=lambda: None, on_error=lambda: None):
        assert sender, "Invalid sender (found %s)" % str(sender)
        self.identifier = sender.next_request_id()
        self.sender = sender
        self.kind = kind
        self.operation = operation
        self.priority = priority
        self.on_accept = on_accept
        self.on_reject = on_reject
        self.on_success = on_success
        self.on_error = on_error
        self.status = self.PENDING
        self._response_time = None
        self._emission_time = None

    @property
    def response_time(self):
        assert self.status == self.OK, "Only successful requests expose a 'response time'"
        return self._response_time

    @property
    def is_pending(self):
        return self.status == self.PENDING

    def send_to(self, service):
        self._emission_time = self.sender.schedule.time_now
        service.schedule.after(self.TRANSMISSION_DELAY, lambda: service.process(self))

    def accept(self):
        self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_accept)

    def reject(self):
        self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_reject)

    def reply_success(self):
        if self.is_pending:
            self.status = self.OK
            assert self._response_time is None, "Response time are updated multiple times!"
            self._response_time = self.sender.schedule.time_now - self._emission_time
            self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_success)

    def reply_error(self):
        if self.is_pending:
            self.status = self.ERROR
            self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_error)

    def discard(self):
        if self.is_pending:
            self.status = self.ERROR
