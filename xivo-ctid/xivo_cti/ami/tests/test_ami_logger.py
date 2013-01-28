# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from xivo_cti.ami import ami_logger
from mock import Mock


class TestAMILogger(unittest.TestCase):

    def setUp(self):
        self.logger = ami_logger.AMILogger.get_instance()

    def tearDown(self):
        pass

    def test_ami_set_logger(self):

        class test_logger(object):
            pass

        self.logger.set_logger(test_logger)

        self.assertEqual(self.logger._logger, test_logger)

    def test_log_ami_event(self):
        event = {'Event': 'LogTest',
                 'First': 'one',
                 'Second': 'two'}

        logger = Mock()
        logger.info = Mock()

        self.logger.set_logger(logger)
        self.logger.log_ami_event(event)

        received = logger.info.call_args[0][0] % logger.info.call_args[0][1]

        self.assertTrue(received.startswith('Event received:'))
        self.assertTrue('Event=>LogTest' in received)
        self.assertTrue('First=>one' in received)
        self.assertTrue('Second=>two' in received)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_ami_logger']
    unittest.main()
