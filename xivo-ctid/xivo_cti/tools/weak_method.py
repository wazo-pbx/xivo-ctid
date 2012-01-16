import weakref

#    http://code.activestate.com/recipes/81253-weakmethod/


class WeakMethodBound(object):

    def __init__(self, function):
        self.function = function.im_func
        self.instance = weakref.ref(function.im_self)

    def __call__(self, *args):
        if self.instance() == None:
            raise TypeError('Method call on a dead object')
        ret = self.function(self.instance(), *args)
        return ret

    def dead(self):
        return self.instance is None or self.instance() is None


class WeakMethodFree(object):

    def __init__(self, function):
        self.function = weakref.ref(function)

    def __call__(self, *arg):
        if self.function() == None:
            raise TypeError('Function no longer exist')
        return (self.function()(*arg))

    def dead(self):
        return self.function is None or self.function() is None


def WeakCallable(function):
    try:
        function.im_func
    except AttributeError:
        return WeakMethodFree(function)
    return WeakMethodBound(function)
