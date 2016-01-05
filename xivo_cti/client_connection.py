# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016 Avencall
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

import logging
import socket
import errno
import ssl

from collections import deque

from xivo_cti import config
from xivo_cti import SSLPROTO

logger = logging.getLogger(__name__)


class ClientConnection(object):
    class CloseException(Exception):
        def __init__(self, errno=-1):
            self.args = (errno,)

    def __init__(self, socket_, address=None):
        self.socket = socket_
        self.address = address
        self.socket.setblocking(0)
        self.sendqueue = deque()
        self.isClosed = False

    def upgrade_ssl(self):
        certfile = config['main']['certfile']
        keyfile = config['main']['keyfile']
        try:
            logger.debug('upgrading socket to ssl\n\tcertfile:  %s\n\tkeyfile: %s', certfile, keyfile)
            self.socket.setblocking(1)
            self.socket.settimeout(0.5)
            self.socket = ssl.wrap_socket(self.socket,
                                          server_side=True,
                                          certfile=certfile,
                                          keyfile=keyfile,
                                          ssl_version=SSLPROTO)
            self.socket.setblocking(0)
        except ssl.SSLError:
            logger.exception('CTI:%s:%d cert=%s key=%s)',
                             self.address[0], self.address[1],
                             certfile,
                             keyfile)
            self.close()

    # useful for select
    def fileno(self):
        return self.socket.fileno()

    def getpeername(self):
        return self.address

    # close socket
    def close(self):
        if not self.isClosed:
            self.isClosed = True
            self.socket.close()

    def append_queue(self, data):
        if self.isClosed:
            raise self.CloseException()
        if data:
            self.sendqueue.append(data)

    # to be called when the socket is ready for writing
    def process_sending(self):
        while self.sendqueue:
            data = self.sendqueue.popleft()
            try:
                n = self.socket.send(data)
                if n == 0:
                    self.sendqueue.appendleft(data)
                    return
                elif n < len(data):  # there is some data left to be sent
                    self.sendqueue.appendleft(data[n:])
            except socket.error, (_errno, string):
                if _errno == errno.EAGAIN:
                    self.sendqueue.appendleft(data)  # try next time !
                    return
                elif _errno in [errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ETIMEDOUT, errno.EHOSTUNREACH]:
                    self.close()
                    raise self.CloseException(_errno)
                elif _errno in [errno.EBADF]:
                    raise self.CloseException(_errno)
                else:
                    raise socket.error(_errno, string)

    # do we have some data to be sent ?
    def need_sending(self):
        return bool(self.sendqueue)

    # to be called when the socked is ready for reading
    def recv(self, bufsize):
        try:
            s = self.socket.recv(bufsize)
            if s:
                return s
            else:
                self.close()
                raise self.CloseException()
        except ssl.SSLError as e:
            if e.args[0] != ssl.SSL_ERROR_WANT_READ:
                raise
        except socket.error as (_errno, _):
            if _errno in [errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ETIMEDOUT, errno.EHOSTUNREACH]:
                self.close()
                raise self.CloseException(_errno)
            elif _errno in [errno.EBADF]:
                # already closed !
                raise self.CloseException(_errno)
            elif _errno != errno.EAGAIN:  # really an error
                raise
        return ''
