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

import base64
import logging
import struct
import urllib2
import zlib

from xivo_cti.tools import variable_substituter as substituter

from xivo_cti.ioc.context import context

logger = logging.getLogger('sheet')

LINE_TEMPLATE = '<internal name="%s"><![CDATA[%s]]></internal>'


class Sheet(object):

    def __init__(self, where, ipbxid, uid):
        self.internaldata = {'where': where,
                             'ipbxid': ipbxid,
                             'uid': uid}
        # config items
        self.options = {}
        self.displays = {}
        # temporary structure
        self.fields = {}
        # output
        self.linestosend = []
        self._variables = context.get('call_form_variable_aggregator').get(uid)

    def setoptions(self, options):
        if options:
            self.options = options

    def setdisplays(self, displays):
        if displays:
            self.displays = displays

    def addinternal(self, varname, varvalue):
        self.linestosend.append(LINE_TEMPLATE % (varname, varvalue))

    def variable_values(self):
        result = {}
        for variable_type, variables in self.channelprops.extra_data.iteritems():
            for variable_name, value in variables.iteritems():
                full_variable_name = '%s-%s' % (variable_type, variable_name)
                result[full_variable_name] = value
        return result

    def resolv_line_content(self, lineprops):
        disabled = lineprops[4] if len(lineprops) == 5 else 0
        if disabled:
            return {}

        title, ftype, default_value, value_to_substitute = lineprops[:4]

        variable_values = self.variable_values()
        finalstring = substituter.substitute_with_default(value_to_substitute,
                                                          default_value,
                                                          variable_values)
        return {'name': title, 'type': ftype, 'contents': finalstring}

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
                    qtui_data = substituter.substitute(qtui_data,
                                                       self.variable_values())
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

    def checkdest(self):
        whom = self.conditions.get('whom')

        tomatch = {}
        data = self._variables
        if whom == 'dest':
            tomatch['desttype'] = data['xivo'].get('desttype')
            tomatch['destid'] = data['xivo'].get('destid')

        return tomatch
