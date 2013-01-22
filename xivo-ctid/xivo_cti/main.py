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

import argparse
import sys
from xivo_cti.ioc.context import context
from xivo_cti.ioc import register_class
from xivo_cti import cti_config


def main():
    _parse_args(sys.argv[1:])

    register_class.setup()

    ctid = context.get('cti_server')
    ctid.setup()
    ctid.run()


def _parse_args(args):
    parser = _new_parser()
    parsed_args = parser.parse_args(args)
    _process_parsed_args(parsed_args)


def _new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-c', '--config')
    parser.add_argument('-C', '--confoverride')
    parser.add_argument('-p', '--pidfile')
    parser.add_argument('-l', '--logfile')
    parser.add_argument('-i', '--ip')
    parser.add_argument('-P', '--portdelta', type=int)
    return parser


def _process_parsed_args(parsed_args):
    if parsed_args.debug:
        cti_config.DEBUG_MODE = parsed_args.debug
    if parsed_args.config:
        cti_config.XIVO_CONF_FILE = parsed_args.config
    if parsed_args.confoverride:
        cti_config.XIVO_CONF_OVER = parsed_args.confoverride
    if parsed_args.pidfile:
        cti_config.PIDFILE = parsed_args.pidfile
    if parsed_args.logfile:
        cti_config.LOGFILENAME = parsed_args.logfile
    if parsed_args.ip:
        cti_config.XIVOIP = parsed_args.ip
    if parsed_args.portdelta:
        cti_config.PORTDELTA = parsed_args.portdelta

    if cti_config.XIVOIP != 'localhost':
        cti_config.XIVO_CONF_FILE = 'https://%s/cti/json.php/restricted/configuration' % cti_config.XIVOIP


if __name__ == '__main__':
    main()
