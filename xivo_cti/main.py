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
    parser.add_argument('-f', '--foreground', action='store_true')
    parser.add_argument('-p', '--pidfile')
    parser.add_argument('-l', '--logfile')
    return parser


def _process_parsed_args(parsed_args):
    if parsed_args.debug:
        cti_config.DEBUG_MODE = parsed_args.debug
    if parsed_args.foreground:
        cti_config.FOREGROUND_MODE = parsed_args.foreground
    if parsed_args.pidfile:
        cti_config.PIDFILE = parsed_args.pidfile
    if parsed_args.logfile:
        cti_config.LOGFILENAME = parsed_args.logfile


if __name__ == '__main__':
    main()
