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

from __future__ import print_function

import argparse
import logging
import os
import time
import sys
import xivo_cti
import yaml

from xivo_dao import cti_service_dao, cti_preference_dao, cti_profile_dao, \
    cti_main_dao, cti_displays_dao, cti_context_dao, cti_phonehints_dao, \
    cti_userstatus_dao, cti_sheets_dao, cti_directories_dao

logger = logging.getLogger('cti_config')

_default_config = {
    'debug': False,
    'foreground': False,
    'pidfile': '/var/run/%s.pid' % xivo_cti.DAEMONNAME,
    'logfile': '/var/log/%s.log' % xivo_cti.DAEMONNAME,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk',
    'config_file': '/etc/xivo-ctid/config.yml',
    'extra_config_files': '/etc/xivo-ctid/conf.d/',
    'bus': {
        'exchange_name': 'xivo-cti',
        'exchange_type': 'direct',
        'exchange_durable': True,
        'binding_key': 'call_form_result',
    },
    'dird': {
        'host': 'localhost',
        'port': 9489,
        'version': 0.1,
    },
}
_cli_config = {}
_db_config = {}
_file_config = {}


# TODO move this function to lib-python
def _parse_config_file(config_file_name):
    try:
        with open(config_file_name) as config_file:
            return yaml.load(config_file)
    except IOError as e:
        print('Could not read config file {}: {}'.format(config_file_name, e), file=sys.stderr)
        return {}


def init_config_file():
    global _file_config

    # The priority of files is based on the file name alphabetical order
    main_config_filename = xivo_cti.config['config_file']
    main_config = _parse_config_file(main_config_filename)

    # the main config file could override the extra config directory
    _file_config = main_config
    update_config()

    extra_config_file_directory = xivo_cti.config['extra_config_files']
    try:
        extra_config_filenames = os.listdir(extra_config_file_directory)
    except OSError:
        extra_config_filenames = []
    configs = [_parse_config_file(f) for f in sorted(extra_config_filenames)]
    configs.append(main_config)

    _file_config = ChainMap(*configs)
    update_config()


def init_cli_config(args):
    parser = _new_parser()
    parsed_args = parser.parse_args(args)
    _process_parsed_args(parsed_args)
    update_config


def update_db_config():
    global _db_config

    db_config = _DbConfig()
    db_config.update()
    _db_config = db_config.getconfig()
    update_config()


def _new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--foreground', action='store_true')
    parser.add_argument('-p', '--pidfile')
    parser.add_argument('-l', '--logfile')
    parser.add_argument('-c', '--config-file', action='store')
    return parser


def _process_parsed_args(parsed_args):
    global _cli_config

    if parsed_args.debug:
        _cli_config['debug'] = parsed_args.debug
    if parsed_args.foreground:
        _cli_config['foreground'] = parsed_args.foreground
    if parsed_args.pidfile:
        _cli_config['pidfile'] = parsed_args.pidfile
    if parsed_args.logfile:
        _cli_config['logfile'] = parsed_args.logfile
    if parsed_args.config_file:
        _cli_config['config_file'] = parsed_args.config_file


class ChainMap(object):

    def __init__(self, *dicts):
        self._dicts = list(dicts)

    def __getitem__(self, key):
        v = self.get(key)
        if v is None:
            raise KeyError('{key} not found'.format(key=key))

        return v

    def __contains__(self, key):
        return self.get(key) is not None

    def get(self, key, default=None):
        for d in self._dicts:
            if key in d:
                return d[key]

        return default


class _DbConfig(object):

    def __init__(self):
        self.xc_json = {}

    def update(self):
        start_time = time.time()
        self.fill_conf()
        logger.info('Config successfully updated in %.6f seconds', (time.time() - start_time))

    def fill_conf(self):
        self.xc_json.update(cti_main_dao.get_config())
        self.xc_json['displays'] = cti_displays_dao.get_config()
        self.xc_json['contexts'] = cti_context_dao.get_config()
        self.xc_json['profiles'] = self._get_profiles()
        self.xc_json['services'] = self._get_services()
        self.xc_json['preferences'] = self._get_preferences()
        self.xc_json['phonestatus'] = cti_phonehints_dao.get_config()
        self.xc_json['userstatus'] = cti_userstatus_dao.get_config()
        self.xc_json['sheets'] = cti_sheets_dao.get_config()
        self.xc_json['directories'] = cti_directories_dao.get_config()

    def _get_profiles(self):
        profiles = cti_profile_dao.get_profiles()
        res = {}
        for profile_key, profile_value in profiles.iteritems():
            new_profile = profile_value
            if 'xlets' in profile_value:
                new_xlet_list = []
                for xlet in profile_value['xlets']:
                    new_xlet = [xlet['name'], xlet['layout']]
                    if xlet['layout'] == 'dock':
                        args = ''
                        args += 'f' if xlet['floating'] else ''
                        args += 'c' if xlet['closable'] else ''
                        args += 'm' if xlet['movable'] else ''
                        args += 's' if xlet['scrollable'] else ''
                        new_xlet.append(args)
                    if xlet['order']:
                        new_xlet.append(str(xlet['order']))
                    new_xlet_list.append(new_xlet)
                    new_profile['xlets'] = new_xlet_list
            res[profile_key] = new_profile
        return res

    def _get_services(self):
        services = cti_service_dao.get_services()
        res = {}
        for service_key, service_value in services.iteritems():
            new_service_key = 'itm_services_%s' % service_key
            new_service_value = [''] if not service_value else service_value
            res[new_service_key] = new_service_value
        return res

    def _get_preferences(self):
        preferences = cti_preference_dao.get_preferences()
        res = {}
        for preference_key, preference_value in preferences.iteritems():
            new_preference_key = 'itm_preferences_%s' % preference_key
            new_preference_value = False if not preference_value else preference_value
            res[new_preference_key] = new_preference_value
        return res

    def getconfig(self):
        return self.xc_json


def update_config():
    xivo_cti.config.data = ChainMap(_cli_config, _file_config, _db_config, _default_config)
