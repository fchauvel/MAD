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

    # Task processing

    def task_created(self, task):
        raise NotImplementedError("Listener::task_created is abstract")

    def task_accepted(self, task):
        raise NotImplementedError("Listener::tack_accepted is abstract")

    def task_rejected(self, task):
        raise NotImplementedError("Listener::task_rejected is abstract")

    def task_assigned_to(self, task, worker):
        raise NotImplementedError("Listener::task_assigned_to is abstract")

    def task_paused(self, task):
        raise NotImplementedError("Listener::task_paused is abstract")

    def task_activated(self, task):
        raise NotImplementedError("Listener::task_activated is abstract")

    def task_successful(self, task):
        raise NotImplementedError("Listener::task_successful is abstract")

    def task_failed(self, task):
        raise NotImplementedError("Listener::task_failed is abstract")

    def task_cancelled(self, task):
        raise NotImplementedError("Listener::task_cancelled is abstract")

    # TODO should be removed carefully!
    def resuming(self, request):
        raise NotImplementedError("Listener::timeout_of is abstract")

    # Outgoing requests

    def posting_of(self, service, request):
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

    # Workers

    def worker_created(self, worker):
        raise NotImplementedError("Listener::worker_created is abstract")

    def worker_busy(self, worker):
        raise NotImplementedError("Listener::worker_busy is abstract")

    def worker_idle(self, worker):
        raise NotImplementedError("Listener::worker_idle is abstract")

    def worker_shutdown(self, worker):
        raise NotImplementedError("Listener::worker_shutdown is abstract")


class Dispatcher:
    """
    Simply dispatch events to other listeners that registered
    """

    def __init__(self):
        self._listeners = set()

    def register(self, listener):
        assert isinstance(listener, Listener), INVALID_LISTENER.format(type(listener))
        self._listeners.add(listener)

    def __getattr__(self, method_name):
        def dispatch(*parameters):
            for each_listener in self._listeners:
                self.__dispatch(each_listener, method_name, *parameters)
        return dispatch

    def __dispatch(self, listener, method_name, *parameters):
        method = getattr(listener, method_name)
        assert method, "Listener {:s} has no method {:s}".format(listener, method_name)
        assert hasattr(method, '__call__'), "{:s} is not a callable!".format(method_name)
        method(*parameters)
