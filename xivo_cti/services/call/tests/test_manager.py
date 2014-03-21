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

from mock import Mock
from mock import sentinel
from unittest import TestCase
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.services.call.call import Call
from xivo_cti.services.call.call import _Channel
from xivo_cti.services.call.manager import CallManager


class TestCallManager(TestCase):

    def setUp(self):
        self.ami = Mock(AMIClass)
        self.manager = CallManager(self.ami)

    def test_when_hangup_then_hangup_destination(self):
        call = Call(
            _Channel(sentinel.source_exten, sentinel.source_channel),
            _Channel(sentinel.destination_exten, sentinel.destination_channel),
        )

        self.manager.hangup(call)

        self.ami.hangup.assert_called_once_with(sentinel.source_channel)
