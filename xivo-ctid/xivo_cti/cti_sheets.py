# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
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

import base64
import logging
import struct
import urllib2
import zlib
import re

logger = logging.getLogger('sheet')

USER_PICTURE_URL = 'http://127.0.0.1/getatt.php?id=%s&obj=user'
LINE_TEMPLATE = '<internal name="%s"><![CDATA[%s]]></internal>'


class Sheet(object):

    def __init__(self, where, ipbxid, channel):
        self.internaldata = {'where': where,
                             'ipbxid': ipbxid,
                             'channel': channel}
        # config items
        self.options = {}
        self.displays = {}
        # temporary structure
        self.fields = {}
        # output
        self.linestosend = []

    def setoptions(self, options):
        if options:
            self.options = options

    def setdisplays(self, displays):
        if displays:
            self.displays = displays

    def addinternal(self, varname, varvalue):
        self.linestosend.append(LINE_TEMPLATE % (varname, varvalue))

    def resolv_line_content(self, lineprops):
        disabled = lineprops[4] if len(lineprops) == 5 else 0
        if disabled:
            return {}

        title, ftype, defaultval, sformat = lineprops[:4]
        data = self.channelprops.extra_data

        def replacement_callback(variable_name):
            try:
                family, name = variable_name.split('-', 1)
            except ValueError:
                logger.warning('Invalid variable %r', variable_name)
                return None
            else:
                try:
                    if family == 'xivo' and name == 'callerpicture':
                        user_id = data['xivo']['userid']
                        return self._get_user_picture(user_id)
                    else:
                        try:
                            value = data[family][name]
                        except KeyError:
                            logger.warning('No value for variable %r', variable_name)
                            return None
                        else:
                            return value if value else None
                except Exception as e:
                    logger.warning('Could not replace variable %r: %s', variable_name, e)
                    return None

        finalstring = _substitute(defaultval, sformat, replacement_callback)
        return {'name': title, 'type': ftype, 'contents': finalstring}

    def _get_user_picture(self, user_id):
        url = USER_PICTURE_URL % user_id
        picture_data = urllib2.urlopen(url).read()
        return base64.b64encode(picture_data)

    def setfields(self):
        for sheetpart, v in self.displays.iteritems():
            self.fields[sheetpart] = {}
            if sheetpart in ['sheet_info', 'systray_info', 'action_info']:
                if not isinstance(v, dict):
                    continue
                for order, vv in v.iteritems():
                    line = self.resolv_line_content(vv)
                    if line:
                        self.fields[sheetpart][order] = line
            elif sheetpart == 'sheet_qtui':
                for order, vv in v.iteritems():
                    try:
                        fobj = urllib2.urlopen(vv)
                        qtui_data = fobj.read().decode('utf8')
                        fobj.close()
                    except Exception:
                        qtui_data = ''
                    self.fields[sheetpart] = {'10': {'name': 'qtui',
                                                     'contents': qtui_data}}
            else:
                logger.warning('sheetpart %s contents %s', sheetpart, v)

    def serialize(self):
        self.makexml()

    def makexml(self):
        self.serial = 'xml'
        self.linestosend = ['<?xml version="1.0" encoding="utf-8"?>',
                            '<profile>',
                            '<user>']
        for k, v in self.internaldata.iteritems():
            self.addinternal(k, v)

        for k, v in self.options.iteritems():
            self.addinternal(k, v)

        # making sure that 'sheet_qtui' is the first in the line, if ever we send it
        # quite long stuff for that, but feel free to shorten it
        sfkeys = self.fields.keys()
        if 'sheet_qtui' in sfkeys:
            sfkeys.pop(sfkeys.index('sheet_qtui'))
            sfkeys.insert(0, 'sheet_qtui')
        for sheetpart in sfkeys:
            v = self.fields.get(sheetpart)
            for order, vv in v.iteritems():
                title = vv.get('name')
                ftype = vv.get('type')
                contents = vv.get('contents')
                self.linestosend.append('<%s order="%04d" name="%s" type="%s"><![CDATA[%s]]></%s>'
                                        % (sheetpart, int(order), title, ftype, contents, sheetpart))
        self.linestosend.extend(['</user>', '</profile>'])

        self.xmlstring = ''.join(self.linestosend).encode('utf8')
        if self.options.get('zip', True):
            ulen = len(self.xmlstring)
            # prepend the uncompressed length in big endian
            # to the zlib compressed string to meet Qt qUncompress() function expectations
            toencode = struct.pack('>I', ulen) + zlib.compress(self.xmlstring)
            self.payload = base64.b64encode(toencode)
            self.compressed = True
        else:
            self.payload = base64.b64encode(self.xmlstring)
            self.compressed = False

    def setconditions(self, conditions):
        self.conditions = conditions

    def checkdest(self, channelprops):
        self.channelprops = channelprops
        whom = self.conditions.get('whom')
        entities = self.conditions.get('entities')
        contexts = self.conditions.get('contexts')
        profileids = self.conditions.get('profileids')

        tomatch = {}
        if profileids:
            tomatch['profileids'] = profileids
        if contexts:
            tomatch['contexts'] = contexts
        if entities:
            tomatch['entities'] = entities

        if whom == 'dest':
            tomatch['desttype'] = channelprops.extra_data.get('xivo').get('desttype')
            tomatch['destid'] = channelprops.extra_data.get('xivo').get('destid')

        return tomatch


def _substitute(default_value, display_value, replacement_callback):
    substituer = _Substituer(replacement_callback)
    return substituer.substitute(default_value, display_value)


class _Substituer(object):

    _VARIABLE_NAME_REGEX = re.compile(r'\{([^}]+)\}')

    def __init__(self, replacement_callback):
        self._nb_substitutions = 0
        self._nb_failed_substitutions = 0
        self._replacement_callback = replacement_callback

    def substitute(self, default_value, display_value):
        substitution_result = self._VARIABLE_NAME_REGEX.sub(self._regex_callback, display_value)
        if self._nb_substitutions == 0:
            return display_value
        elif self._nb_failed_substitutions == self._nb_substitutions:
            return default_value if default_value else display_value
        else:
            return substitution_result

    def _regex_callback(self, m):
        variable_name = m.group(1)
        variable_value = self._replacement_callback(variable_name)
        self._nb_substitutions += 1
        if variable_value is None:
            self._nb_failed_substitutions += 1
            return ''
        else:
            return str(variable_value)
