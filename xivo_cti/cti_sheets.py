# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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

    def setoptions(self, options):
        if options:
            self.options = options

    def setdisplays(self, displays):
        if displays:
            self.displays = displays

    def addinternal(self, varname, varvalue):
        self.linestosend.append(LINE_TEMPLATE % (varname, varvalue))

    def variable_values(self):
        variables = context.get('call_form_variable_aggregator').get(self.internaldata['uid'])
        result = {}
        for variable_type, variables in variables.iteritems():
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
                ui_file_path = v
                if not ui_file_path:
                    continue
                try:
                    ui_file = urllib2.urlopen(ui_file_path)
                    qtui_data = ui_file.read().decode('utf8')
                    ui_file.close()
                    qtui_data = substituter.substitute(qtui_data, self.variable_values())
                    self.fields[sheetpart] = {'10': {'name': 'qtui', 'contents': qtui_data}}
                except Exception as e:
                    logger.error('Could not read UI file %s: %s', ui_file_path, unicode(str(e), 'utf8'))
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
        data = self.variable_values()
        if whom == 'dest':
            tomatch['desttype'] = data.get('xivo-desttype')
            tomatch['destid'] = data.get('xivo-destid')

        return tomatch
