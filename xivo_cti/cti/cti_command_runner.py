# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.exception import InvalidCallbackException
from xivo_cti.cti.cti_reply_generator import CTIReplyGenerator

logger = logging.getLogger('CTICommandRunner')


class CTICommandRunner(object):

    def __init__(self):
        self._reply_generator = CTIReplyGenerator()

    def _get_arguments(self, command, args):
        return [getattr(command, arg) for arg in args]

    def run(self, command):
        for callback in command.callbacks_with_params():
            function, args = callback
            arg_list = self._get_arguments(command, args)
            try:
                reply = function(*arg_list)
            except InvalidCallbackException as e:
                logger.debug('failed to dispatch cti command "%s" to callback "%s": "%s"', command, callback, e)
                command.deregister_callback(function)
                continue
            if reply:
                return self._reply_generator.get_reply(reply[0], command, reply[1], reply[2] if len(reply) >= 3 else False)
        return {'status': 'OK'}
