# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import weakref

from xivo_cti.exception import InvalidCallbackException

#    http://code.activestate.com/recipes/81253-weakmethod/


class WeakMethodBound(object):

    def __init__(self, function):
        self.function = function.im_func
        self.instance = weakref.ref(function.im_self)

    def __call__(self, *args):
        if self.instance() is None:
            raise InvalidCallbackException('Method call on a dead object')
        ret = self.function(self.instance(), *args)
        return ret

    def __eq__(self, other):
        return hasattr(other, 'instance') and self.instance() == other.instance() and self.function == other.function

    def dead(self):
        return self.instance is None or self.instance() is None


class WeakMethodFree(object):

    def __init__(self, function):
        self.function = weakref.ref(function)

    def __call__(self, *arg):
        if self.function() is None:
            raise InvalidCallbackException('Function no longer exist')
        return (self.function()(*arg))

    def __eq__(self, other):
        return self.function() == other.function()

    def dead(self):
        return self.function is None or self.function() is None


def WeakCallable(function):
    try:
        function.im_func
    except AttributeError:
        return WeakMethodFree(function)
    return WeakMethodBound(function)
