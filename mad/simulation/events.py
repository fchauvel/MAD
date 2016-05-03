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

INVALID_LISTENER = "Only 'Listener' objects may register (found '{0!s}')"


class Listener:
    """
    Events emitted by a service during the the simulation
    """

    # Incoming request

    def task_created(self, request):
        raise NotImplementedError("Listener::task_created is abstract")

    def task_rejected(self, request):
        raise NotImplementedError("Listener::rejection_of is abstract")

    def task_successful(self, request):
        raise NotImplementedError("Listener::task_successful is abstract")

    def task_failed(self, request):
        raise NotImplementedError("Listener::task_failed is abstract")

    def task_ready(self, request):
        raise NotImplementedError("Listener::task_ready is abstract")

    def task_running(self, request):
        raise NotImplementedError("Listener::timeout_of is abstract")

    # TODO should be removed
    def resuming(self, request):
        raise NotImplementedError("Listener::timeout_of is abstract")

    # Outgoing requests

    def posting_of(self, request):
        raise NotImplementedError("Listener::posting_of is abstract")

    def acceptance_of(self, request):
        raise NotImplementedError("Listener::acceptance_of is abstract")

    def rejection_of(self, request):
        raise NotImplementedError("Listener::rejection_of is abstract")

    def success_of(self, request):
        raise NotImplementedError("Listener::success_of is abstract")

    def failure_of(self, request):
        raise NotImplementedError("Listener::failure_of is abstract")

    def timeout_of(self, request):
        raise NotImplementedError("Listener::timeout_of is abstract")


class Dispatcher(Listener):
    """
    Simply dispatch events to other listeners that registered
    """

    def __init__(self):
        self._listeners = set()

    def register(self, listener):
        assert isinstance(listener, Listener), INVALID_LISTENER.format(type(listener))
        self._listeners.add(listener)

    def task_created(self, request):
        self._dispatch(self.task_created.__name__, request)

    def task_rejected(self, request):
        self._dispatch(self.task_rejected.__name__, request)

    def task_failed(self, request):
        self._dispatch(self.task_failed.__name__, request)

    def task_successful(self, request):
        self._dispatch(self.task_successful.__name__, request)

    def task_ready(self, request):
        self._dispatch(self.task_ready.__name__, request)

    def task_running(self, request):
        self._dispatch(self.task_running.__name__, request)

    def resuming(self, request):
        self._dispatch(self.resuming.__name__, request)

    def posting_of(self, service, request):
        self._dispatch(self.posting_of.__name__, service, request)

    def acceptance_of(self, request):
        self._dispatch(self.acceptance_of.__name__, request)

    def rejection_of(self, request):
        self._dispatch(self.rejection_of.__name__, request)

    def success_of(self, request):
        self._dispatch(self.success_of.__name__, request)

    def failure_of(self, request):
        self._dispatch(self.failure_of.__name__, request)

    def timeout_of(self, request):
        self._dispatch(self.timeout_of.__name__, request)

    def _dispatch(self, method, *parameters):
        for each_listener in self._listeners:
            delegate = getattr(each_listener, method)
            delegate(*parameters)

