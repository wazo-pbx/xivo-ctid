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

import threading


class Scheduler(object):

    def __init__(self, task_queue):
        self._task_queue = task_queue

    def schedule(self, timeout, callback_function, *callback_args):
        callback_args_extended = [callback_function]
        callback_args_extended.extend(callback_args)
        timer = threading.Timer(timeout, self._task_queue.put, callback_args_extended)
        timer.start()
