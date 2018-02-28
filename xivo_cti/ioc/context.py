# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

"""
Non-invasive Dependency Injection Container.
It fills given constructors or factory methods
based on their named arguments.

See the demo usage at the end of file.

Author: Ivo Danihelka
Source: http://code.activestate.com/recipes/576609/
License: MIT
"""

NO_DEFAULT = "NO_DEFAULT"


class Context:
    """A depencency injection container.
    It detects the needed dependencies based on arguments of factories.
    """

    def __init__(self):
        """Creates empty context.
        """
        self.instances = {}
        self.factories = {}

    def register(self, property, factory, *factory_args, **factory_kw):
        """Registers factory for the given property name.
        The factory could be a callable or a raw value.
        Arguments of the factory will be searched
        inside the context by their name.

        The factory_args and factory_kw allow
        to specify extra arguments for the factory.
        """
        if (factory_args or factory_kw) and not callable(factory):
            raise ValueError(
                "Only callable factory supports extra args: %s, %s(%s, %s)"
                % (property, factory, factory_args, factory_kw))

        self.factories[property] = factory, factory_args, factory_kw

    def reset(self):
        self.instances = {}
        self.factories = {}

    def get(self, property):
        """Lookups the given property name in context.
        Raises KeyError when no such property is found.
        """
        if property not in self.factories:
            raise KeyError("No factory for: %s", property)

        if property in self.instances:
            return self.instances[property]

        factory_spec = self.factories[property]
        instance = self._instantiate(property, *factory_spec)
        self.instances[property] = instance
        return instance

    def get_all(self):
        """Returns instances of all properties.
        """
        return [self.get(name) for name in self.factories.iterkeys()]

    def build(self, factory, *factory_args, **factory_kw):
        """Invokes the given factory to build a configured instance.
        """
        return self._instantiate("", factory, factory_args, factory_kw)

    def _instantiate(self, name, factory, factory_args, factory_kw):
        if not callable(factory):
            return factory

        kwargs = self._prepare_kwargs(factory, factory_args, factory_kw)
        return factory(*factory_args, **kwargs)

    def _prepare_kwargs(self, factory, factory_args, factory_kw):
        """Returns keyword arguments usable for the given factory.
        The factory_kw could specify explicit keyword values.
        """
        defaults = get_argdefaults(factory, len(factory_args))

        for arg, default in defaults.iteritems():
            if arg in factory_kw:
                continue
            elif arg in self.factories:
                defaults[arg] = self.get(arg)
            elif default is NO_DEFAULT:
                raise KeyError("No factory for arg: %s" % arg)

        defaults.update(factory_kw)
        return defaults


def get_argdefaults(factory, num_skipped=0):
    """Returns dict of (arg_name, default_value) pairs.
    The default_value could be NO_DEFAULT
    when no default was specified.
    """
    args, defaults = _getargspec(factory)

    if defaults is not None:
        num_without_defaults = len(args) - len(defaults)
        default_values = (NO_DEFAULT,) * num_without_defaults + defaults
    else:
        default_values = (NO_DEFAULT,) * len(args)

    return dict(zip(args, default_values)[num_skipped:])


def _getargspec(factory):
    """Describes needed arguments for the given factory.
    Returns tuple (args, defaults) with argument names
    and default values for args tail.
    """
    import inspect
    if inspect.isclass(factory):
        factory = factory.__init__

    try:
        if inspect.ismethod(factory):
            args, vargs, vkw, defaults = inspect.getargspec(factory)
            args = args[1:]
        elif inspect.isfunction(factory):
            args, vargs, vkw, defaults = inspect.getargspec(factory)
        else:
            args, defaults = [], None
        return args, defaults
    except TypeError:
        raise Exception('The function "%s" does not exist' % factory.__name__)


context = Context()


if __name__ == "__main__":
    class Demo:
        def __init__(self, title, user, console):
            self.title = title
            self.user = user
            self.console = console

        def say_hello(self):
            self.console.println("*** IoC Demo ***")
            self.console.println(self.title)
            self.console.println("Hello %s" % self.user)

    class Console:
        def __init__(self, prefix=""):
            self.prefix = prefix

        def println(self, message):
            print self.prefix, message

    ctx = Context()
    ctx.register("user", "some user")
    ctx.register("console", Console, "-->")
    demo = ctx.build(Demo, title="Inversion of Control")

    demo.say_hello()
