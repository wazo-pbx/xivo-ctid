# XiVO CTI Server
# vim: set fileencoding=utf-8

# Copyright (C) 2007-2011  Avencall
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
import urllib2
import cjson
import ssl
import string
import time

logger = logging.getLogger('cti_config')


DAEMONNAME = 'xivo-ctid'
BUFSIZE_LARGE = 262144
DEBUG_MODE = False
LOGFILENAME = '/var/log/%s.log' % DAEMONNAME
PIDFILE = '/var/run/%s.pid' % DAEMONNAME
PORTDELTA = 0
SSLPROTO = ssl.PROTOCOL_TLSv1
XIVOIP = 'localhost'
XIVO_CONF_FILE = 'http://localhost/cti/json.php/private/configuration'
XIVO_CONF_FILE_DEFAULT = 'file:///etc/pf-xivo/xivo-ctid/default_config.json'
CTI_PROTOCOL_VERSION = '1.2'
ALPHANUMS = string.uppercase + string.lowercase + string.digits


class Config(object):
    instance = None

    def __init__(self, * urilist):
        self.urilist = urilist
        self.ipwebs = XIVOIP
        self.xc_json = {}
        self._context_separation = None

    def update(self):
        # the aim of the urilist would be to handle the URI's one after the other
        # when there is a reachability issue (like it can happen in first steps ...)
        self.update_uri(self.urilist[0])

    def update_uri(self, uri):
        if uri.find('json') < 0:
            return
        if uri.find(':') < 0:
            return

        got_webi_answer = False
        while not got_webi_answer:
            try:
                response = urllib2.urlopen(uri)
                self.json_config = response.read().replace('\/', '/')
                self.xc_json = cjson.decode(self.json_config)
                got_webi_answer = True
            except Exception:
                logger.warning('Waiting for XiVO web services')
                time.sleep(5)

        for profdef in self.xc_json.get('profiles', {}).itervalues():
            if profdef['xlets']:
                for xlet_attr in profdef['xlets']:
                    if 'N/A' in xlet_attr:
                        xlet_attr.remove('N/A')
                    # XXX what should be done when 'tabber' is in xlet_attr ?
                    #     this was currently a no-op due to what looked like a
                    #     programming bug
                    if 'tab' in xlet_attr:
                        del xlet_attr[2]
                    if xlet_attr[1] == 'grid':
                        del xlet_attr[2]

    def getconfig(self, key=None):
        if key:
            ret = self.xc_json.get(key, {})
        else:
            ret = self.xc_json
        return ret

    def set_context_separation(self, context_separation=None):
        if context_separation:
            self._context_separation = context_separation
        else:
            self._context_separation = False
        logger.debug('Context separation: %s', self._context_separation)

    def part_context(self):
        return self._context_separation == True

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls(XIVO_CONF_FILE, XIVO_CONF_FILE_DEFAULT)
        return cls.instance
