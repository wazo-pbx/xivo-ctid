# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import fcntl
import os
import threading

from xivo_cti.task import new_task


def new_task_queue():
    return _TaskQueue(_PollableQueue(_SignallableFileDescriptor()))


class _TaskQueue(object):

    def __init__(self, pollable_queue):
        self._pollable_queue = pollable_queue

    def close(self):
        self._pollable_queue.close()

    def clear(self):
        self._pollable_queue.get_all()

    def put(self, function, *args):
        self.put_task(new_task(function, args))

    def put_task(self, task):
        self._pollable_queue.put(task)

    def run(self):
        for task in self._pollable_queue.get_all():
            # XXX if there's more than 1 task and a non-last task raise an
            #     exception, than right now the remaining tasks will never be
            #     run, which could be quite bad
            task()

    def fileno(self):
        return self._pollable_queue.fileno()


class _PollableQueue(object):

    def __init__(self, signallable_fd):
        self._signallable_fd = signallable_fd
        self._lock = threading.Lock()
        self._items = []

    def close(self):
        self._signallable_fd.close()

    def put(self, item):
        with self._lock:
            if not self._items:
                self._signallable_fd.signal()
            self._items.append(item)

    def get_all(self):
        with self._lock:
            if self._items:
                self._signallable_fd.clear()
            items = self._items
            self._items = []
        return items

    def fileno(self):
        return self._signallable_fd.fileno()


class _SignallableFileDescriptor(object):

    def __init__(self):
        self._read_fd, self._write_fd = os.pipe()
        self._set_flags(self._read_fd)
        self._set_flags(self._write_fd)

    def _set_flags(self, fd):
        self._set_fd_flags(fd)
        self._set_fl_flags(fd)

    def _set_fd_flags(self, fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        flags = flags | fcntl.FD_CLOEXEC
        fcntl.fcntl(fd, fcntl.F_SETFD, flags)

    def _set_fl_flags(self, fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def close(self):
        os.close(self._read_fd)
        os.close(self._write_fd)

    def clear(self):
        os.read(self._read_fd, 256)

    def signal(self):
        os.write(self._write_fd, '0000')

    def fileno(self):
        return self._read_fd
