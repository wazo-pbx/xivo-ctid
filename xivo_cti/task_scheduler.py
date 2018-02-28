# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import heapq
import time

from xivo_cti.task import Task


def new_task_scheduler():
    return _TaskScheduler(time.time)


class _TaskScheduler(object):

    def __init__(self, time_function):
        self._time_function = time_function
        self._tasks = []

    def clear(self):
        self._tasks = []

    def schedule(self, secs, function, *args):
        task = _ScheduledTask(self._time_function() + secs, function, args)
        heapq.heappush(self._tasks, task)
        return task

    def timeout(self):
        # Return None if no task, 0 is the next task is in the past
        self._pop_cancelled_tasks()
        if not self._tasks:
            return None

        task = self._tasks[0]
        diff = task._abs_time - self._time_function()
        if diff < 0.0:
            diff = 0.0
        return diff

    def run(self, delta=0.005):
        now = self._time_function() + delta
        while self._tasks:
            task = self._tasks[0]
            if task._abs_time >= now:
                return

            heapq.heappop(self._tasks)
            if task._cancelled:
                continue

            task.run()

    def _pop_cancelled_tasks(self):
        while self._tasks and self._tasks[0]._cancelled:
            heapq.heappop(self._tasks)


class _ScheduledTask(Task):

    def __init__(self, abs_time, function, args):
        super(_ScheduledTask, self).__init__(function, args)
        self._abs_time = abs_time
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def __lt__(self, other):
        return self._abs_time < other._abs_time
