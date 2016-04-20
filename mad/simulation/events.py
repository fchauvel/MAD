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

    def arrival_of(self, request):
        raise NotImplementedError("Listener::arrival_of is abstract")

    def rejection_of(self, request):
        raise NotImplementedError("Listener::rejection_of is abstract")

    def posting_of(self, request):
        raise NotImplementedError("Listener::posting_of is abstract")

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
        assert isinstance(listener, Listener),INVALID_LISTENER.format(type(listener))
        self._listeners.add(listener)

    def arrival_of(self, request):
        self._dispatch("arrival_of", request)

    def rejection_of(self, request):
        self._dispatch("rejection_of", request)

    def posting_of(self, request):
        self._dispatch("posting_of", request)

    def success_of(self, request):
        self._dispatch("success_of", request)

    def failure_of(self, request):
        self._dispatch("failure_of", request)

    def timeout_of(self, request):
        self._dispatch("timeout_of", request)

    def _dispatch(self, method, *parameters):
        for each_listener in self._listeners:
            delegate = getattr(each_listener, method)
            delegate(*parameters)

