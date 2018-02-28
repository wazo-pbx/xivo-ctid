# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import fcntl
import os
import threading

from xivo_cti.task import Task


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
        self._pollable_queue.put(Task(function, args))

    def run(self):
        for task in self._pollable_queue.get_all():
            task.run()

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
