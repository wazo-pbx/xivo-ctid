#!/usr/bin/python
# vim: set fileencoding=utf-8 :

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

import unittest
from xivo_cti.services.meetme_service_notifier import MeetmeServiceNotifier

import Queue


class TestMeetmeServiceNotifier(unittest.TestCase):
    def setUp(self):
        self.ipbx_id = 'xivo_test'
        self.notifier = MeetmeServiceNotifier()
        self.notifier.events_cti = Queue.Queue()
        self.notifier.ipbx_id = self.ipbx_id

    def tearDown(self):
        pass

    def test_prepare_message(self):
        result = self.notifier._prepare_message()

        self.assertEqual(result['tipbxid'], 'xivo_test')

    def test_add(self):
        meetme_id = 64
        expected = {"class": "getlist",
                    "function": "addconfig",
                    "listname": "meetmes",
                    "tipbxid": self.ipbx_id,
                    'list': [meetme_id]}

        self.notifier.add(meetme_id)

        self.assertTrue(self.notifier.events_cti.qsize() > 0)
        event = self.notifier.events_cti.get()
        self.assertEqual(event, expected)
