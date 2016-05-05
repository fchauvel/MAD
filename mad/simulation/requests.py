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

from enum import Enum

from mad.evaluation import Error, Success


class RequestStatus(Enum):
    PENDING, OK, ERROR, ACCEPTED, REJECTED = range(5)


class Request:
    TRANSMISSION_DELAY = 1

    def __init__(self, task, operation, priority, continuation):
        assert task, "Invalid task (found None)"
        self.task = task
        self.operation = operation
        self.priority = priority
        self.continuation = continuation
        self.identifier = self.sender.next_request_id()
        self.status = RequestStatus.PENDING
        self._response_time = None
        self._emission_time = None

    @property
    def sender(self):
        return self.task.service

    def __repr__(self):
        return "Req. %d" % self.identifier

    @property
    def response_time(self):
        assert self.status == RequestStatus.OK, "Only successful requests expose a 'response time'"
        return self._response_time

    @property
    def is_pending(self):
        return self.status == RequestStatus.PENDING

    def send_to(self, service):
        self.sender.listener.posting_of(service.name, self)
        self._emission_time = self.sender.schedule.time_now
        service.schedule.after(self.TRANSMISSION_DELAY, lambda: service.process(self))

    def accept(self):
        self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_accept)

    def reject(self):
        if self.is_pending:
            self.status = RequestStatus.ERROR
            self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_reject)

    def reply(self, task, status):
        if not self.is_pending: # Should be has_been_discarded
            task.discard()
        elif status.is_successful:
            self.reply_success()
            task.succeed()
        else:
            self.reply_error()
            task.fail()

    def reply_success(self):
        if self.is_pending:
            self.status = RequestStatus.OK
            assert self._response_time is None, "Response time are updated multiple times!"
            self._response_time = self.sender.schedule.time_now - self._emission_time
            self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_success)

    def reply_error(self):
        if self.is_pending:
            self.status = RequestStatus.ERROR
            self.sender.schedule.after(self.TRANSMISSION_DELAY, self.on_error)

    def discard(self):
        if self.is_pending:
            self.status = RequestStatus.ERROR

    def on_reject(self):
        pass

    def on_accept(self):
        pass

    def on_success(self):
        pass

    def on_error(self):
        pass

    def finalise(self, task, status):
        pass


class Query(Request):

    def __init__(self, task, operation, priority, continuation):
        super().__init__(task, operation, priority, continuation)

    def on_accept(self):
        self.task.service.listener.acceptance_of(self)

    def on_reject(self):
        self.task.service.listener.rejection_of(self)
        self.task.resume_with(lambda worker: self.continuation(Error()))

    def on_success(self):
        self.task.service.listener.success_of(self)
        self.task.resume_with(lambda worker: self.continuation(Success()))

    def on_error(self):
        self.task.service.listener.failure_of(self)
        self.task.resume_with(lambda worker: self.continuation(Error()))

    def finalise(self, task, status):
        task.compute(1, lambda: self.reply(task, status))


class Trigger(Request):

    def __init__(self, task, operation, priority, continuation):
        super().__init__(task, operation, priority, continuation)

    def on_reject(self):
        self.task.service.listener.rejection_of(self)
        self.task.resume_with(lambda worker: self.continuation(Error()))

    def on_accept(self):
        self.task.service.listener.acceptance_of(self)
        self.task.resume_with(lambda worker: self.continuation(Success()))

    def finalise(self, task, status):
        self.reply(task, status)
