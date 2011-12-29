# vim: set fileencoding=utf-8 :
# xivo-ctid

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

from xivo_cti.ami import ami_logger


class Test(unittest.TestCase):

    def setUp(self):
        self.logger = ami_logger.AMILogger.get_instance()

    def tearDown(self):
        pass

    def test_ami_set_logger(self):
        def func(msg):
            print msg

        self.logger.set_logger(func)

        self.assertEqual(self.logger._log, func)

    def test_log_ami_event(self):
        event = {'Event': 'LogTest',
                 'First': 'one',
                 'Second': 'two'}

        def func(msg):
            self.assertTrue(msg.startswith('Event received:'))
            self.assertTrue('Event=>LogTest' in msg)
            self.assertTrue('First=>one' in msg)
            self.assertTrue('Second=>two' in msg)

        self.logger.set_logger(func)
        self.logger.log_ami_event(event)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_ami_logger']
    unittest.main()
