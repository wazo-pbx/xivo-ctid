# vim: set fileencoding=utf-8 :
# xivo-ctid

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from xivo_cti.ami import ami_callback_handler


class AMILogger(object):
    _instance = None
    logged_events = ('Dial',
                     'Bridge',
                     'FullyBooted',
                     'Shutdown')

    def __init__(self):
        self._logger = None

    def set_logger(self, logger):
        self._logger = logger

    def log_ami_event(self, event):
        msg = ('Event received:%s' %
               ' '.join(['%s=>%s' % (key, value) for key, value in event.iteritems()]))
        self._logger.log.info(msg)

    @classmethod
    def register_callbacks(cls):
        callback_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        logger = cls.get_instance()
        for event_name in cls.logged_events:
            callback_handler.register_callback(event_name, logger.log_ami_event)

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = AMILogger()
            cls._instance.set_logger(logging.getLogger('AMI logger'))
        return cls._instance
