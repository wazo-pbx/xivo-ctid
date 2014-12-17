# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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

import socket
import errno
import ssl
from collections import deque
from xivo_cti import BUFSIZE_LARGE


class ClientConnection(object):
    class CloseException(Exception):
        def __init__(self, errno= -1):
            self.args = (errno,)

    def __init__(self, socket, address=None, sep='\n'):
        self.socket = socket
        self.address = address
        self.socket.setblocking(0)
        self.sendqueue = deque()
        self.readbuff = ''
        self.isClosed = False
        self.separator = sep

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
        data = self._reset_sendqueue()
        try:
            n = self.socket.send(data)
            if n < len(data):
                self.sendqueue.append(data[n:])
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

    def _reset_sendqueue(self):
        data = ''.join(self.sendqueue)
        self.sendqueue.clear()
        return data

    # do we have some data to be sent ?
    def need_sending(self):
        return bool(self.sendqueue)

    # to be called when the socked is ready for reading
    def recv(self):
        try:
            s = self.socket.recv(BUFSIZE_LARGE)
            if s:
                self.readbuff += s
            else:
                # remote host closed the connection
                self.close()
                raise self.CloseException()
        except ssl.SSLError as e:
            if e.args[0] != ssl.SSL_ERROR_WANT_READ:
                raise
        except socket.error, (_errno, string):
            if _errno in [errno.EPIPE, errno.ECONNRESET, errno.ENOTCONN, errno.ETIMEDOUT, errno.EHOSTUNREACH]:
                self.close()
                raise self.CloseException(_errno)
            elif _errno in [errno.EBADF]:
                # already closed !
                raise self.CloseException(_errno)
            elif _errno != errno.EAGAIN:  # really an error
                raise

    # return a line if available or None
    # use the separator to split "lines"
    def readline(self):
        self.recv()
        try:
            k = self.readbuff.index(self.separator)
            ret = self.readbuff[0:k + 1]
            self.readbuff = self.readbuff[k + 1:]
            return ret
        except:
            return None

    # return lines if available, None otherwise
    # use the separator to split "lines"
    def readlines(self):
        ret = list()
        self.recv()
        try:
            ret = self.readbuff.split(self.separator)
            self.readbuff = ret.pop()
        except:
            pass
        return ret
