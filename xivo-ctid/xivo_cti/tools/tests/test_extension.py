# vim: set fileencoding=utf-8 :
# XiVO CTI Server

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

from xivo_cti.tools.extension import normalize_exten

class TestExtension(unittest.TestCase):
    def test_normalize_exten(self):
        extens = ['00.11.22.33.44',
                  '00 11 22 33 44',
                  '00-+_11@%^& 22":<>/33?:";44']
        for exten in extens:
            self.assertEqual(normalize_exten(exten), '0011223344')

    def test_normalize_exten_any_valid_char(self):
        exten = '-+@%^& ":<>/?:";'
        self.assertEqual(normalize_exten(exten), None)
