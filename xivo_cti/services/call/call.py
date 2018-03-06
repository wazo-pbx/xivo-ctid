# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


class _Channel(object):
    """
    The _Channel class is package private to the call package and it's _private
    fields should not be used outside the package
    """

    def __init__(self, extension, channel):
        self.extension = extension
        self._channel = channel

    def __eq__(self, other):
        return self.extension == other.extension and self._channel == other._channel

    def __repr__(self):
        return '{name}({extension}, {channel})'.format(name=self.__class__.__name__,
                                                       extension=self.extension,
                                                       channel=self._channel)


class Call(object):

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __str__(self):
        return '{name} from {source} to {destination}'.format(**self._info())

    def _info(self):
        return {'name': self.__class__.__name__,
                'source': self.source,
                'destination': self.destination}

    @property
    def is_internal(self):
        return (self.source.extension.is_internal and
                self.destination.extension.is_internal)

    def __eq__(self, compared_call):
        return self._is_equal(compared_call)

    def __ne__(self, compared_call):
        return not self._is_equal(compared_call)

    def _is_equal(self, compared_call):
        return (self.source == compared_call.source and
                self.destination == compared_call.destination)
