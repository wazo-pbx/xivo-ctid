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

import base64
import logging
import struct
import urllib2
import zlib
import re

logger = logging.getLogger('sheet')

FORMAT_STRING_PATTERN = re.compile(r'\{\w+\-\w+\}')
USER_PICTURE_URL = 'http://127.0.0.1/getatt.php?id=%s&obj=user'


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
        self.linestosend.append('<internal name="%s"><![CDATA[%s]]></internal>'
                                % (varname, varvalue))

    def resolv_line_content(self, lineprops):
        disabled = lineprops[4] if len(lineprops) == 5 else 0
        [title, ftype, defaultval, sformat] = lineprops[:4]

        if disabled:
            return {}

        try:
            family, name = split_format_string(sformat)
            data = self.channelprops.extra_data
            if family == 'xivo' and name == 'callerpicture':
                user_id = data['xivo']['userid']
                finalstring = self._get_user_picture(user_id)
            else:
                finalstring = data[family][name]
        except Exception:
            logger.warning('Could not extract format string %s', sformat)
            finalstring = defaultval

        result = {'name': title,
                  'type': ftype,
                  'contents': finalstring}

        return result

    def _get_user_picture(self, user_id):
        url = USER_PICTURE_URL % userid
        with urllib2.urlopen(url) as fobj:
            picture_data = fobj.read()
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
                    self.fields[sheetpart] = {'10' : {'name' : 'qtui',
                                                      'contents' : qtui_data}}
            else:
                logger.warning('sheetpart %s contents %s', sheetpart, v) 
        # print self.fields
        # linestosend.extend(self.__build_xmlqtui__('sheet_qtui', actionopt, itemdir))

    def serialize(self):
        if True:
            self.makexml()
        else:
            self.makejson()

    def makexml(self):
        self.serial = 'xml'
        self.linestosend = []
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

    def makejson(self):
        self.serial = 'json'
        self.compressed = False
        self.payload = { 'internal' : self.internaldata,
                         'fields' : self.fields }

    def setconditions(self, conditions):
        self.conditions = conditions

    def checkdest(self, channelprops):
        self.channelprops = channelprops
        whom = self.conditions.get('whom')
        entities = self.conditions.get('entities')
        contexts = self.conditions.get('contexts')
        profileids = self.conditions.get('profileids')

        tomatch = dict()
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


def split_format_string(format_string):
    if not FORMAT_STRING_PATTERN.match(format_string):
        raise ValueError('Invalid format string: %s', format_string)

    return format_string[1:-1].split('-', 1)
