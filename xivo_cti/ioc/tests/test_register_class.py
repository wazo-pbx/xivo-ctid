# -*- coding: utf-8 -*-

# Copyright (C) 2009-2014 Avencall
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

import unittest
from xivo_cti.ioc.context import context
from xivo_cti.ioc import register_class


class Test(unittest.TestCase):

    def test_get_context(self):
        register_class.setup()

        config = context.get('cti_config')
        config.xc_json = {
            'main': {
                'live_reload_conf': True
            },
            'ipbx': {
                'ipbx_connection': {
                    'ipaddress': '127.0.0.1',
                    'ipport': 5038,
                    'loginname': 'xivouser',
                    'password': 'xivouser'
                }
            }
        }

        context.get_all()
