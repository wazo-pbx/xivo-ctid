# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return self.function.__name__

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
        return hasattr(other, 'function') and self.function() == other.function()

    def __ne__(self, other):
        return not self == other

    def dead(self):
        return self.function is None or self.function() is None


def WeakCallable(function):
    try:
        function.im_func
    except AttributeError:
        return WeakMethodFree(function)
    return WeakMethodBound(function)
