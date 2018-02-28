# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)

_classes_by_class_name = {}
_getlist_classes_by_fun_name = {}


def register_class(klass):
    class_name = klass.class_name
    if class_name == 'getlist':
        raise Exception('getlist class can\'t be registered here')
    elif class_name in _classes_by_class_name:
        _classes_by_class_name[class_name].append(klass)
    else:
        _classes_by_class_name[class_name] = [klass]


def register_getlist_class(klass, function_name):
    if function_name in _getlist_classes_by_fun_name:
        raise Exception('getlist class already registered for %r' % function_name)

    _getlist_classes_by_fun_name[function_name] = [klass]


def get_class(msg):
    class_name = msg['class']
    if class_name == 'getlist':
        return _get_class_getlist(msg)
    else:
        return _get_class_generic(class_name, msg)


def _get_class_getlist(msg):
    function_name = msg['function']
    try:
        return _getlist_classes_by_fun_name[function_name]
    except KeyError:
        # since there is two "registry" system in parallel, this one and the
        # one in xivo_cti.cti_command (old), this may be a normal case
        logger.debug('No getlist class in registry for function %r', function_name)
        return []


def _get_class_generic(class_name, msg):
    try:
        classes = _classes_by_class_name[class_name]
    except KeyError:
        # since there is two "registry" system in parallel, this one and the
        # one in xivo_cti.cti_command (old), this may be a normal case
        logger.debug('No class in registry for class %r', class_name)
        return []
    else:
        return [klass for klass in classes if klass.match_message(msg)]
