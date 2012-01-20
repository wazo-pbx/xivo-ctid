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

from xivo_cti.cti.commands.directory import Directory
from xivo_cti.cti.cti_command import CTICommand


class TestDirectory(unittest.TestCase):

    _command_id = 1171069123
    _pattern = 'Test'
    _msg_dict = {CTICommand.CLASS: Directory.COMMAND_CLASS,
                 CTICommand.COMMANDID: _command_id,
                 Directory.PATTERN: _pattern}

    def test_directory(self):
        self.assertEqual(Directory.COMMAND_CLASS, 'directory')

        directory = Directory()

        self.assertEqual(directory.command_class, Directory.COMMAND_CLASS)
        self.assertEqual(directory.commandid, None)
        self.assertEqual(directory.pattern, None)

    def test_from_dict(self):
        directory = Directory.from_dict(self._msg_dict)

        self.assertEqual(directory.command_class, Directory.COMMAND_CLASS)
        self.assertEqual(directory.commandid, self._command_id)
        self.assertEqual(directory.pattern, self._pattern)

    def test_get_reply_list(self):
        headers = ['Nom', u'Numéro', 'Entreprise', 'E-mail', 'Source']
        results = [u"Père Noël;102;Inconnue;;Répertoire XiVO Interne",
                   u"Pépé L'Igüane;103;Inconnue;;Répertoire XiVO Interne",
                   u"Pascal Cadotte Michaud;100;Inconnue;;Répertoire XiVO Interne"]
        directory = Directory.from_dict(self._msg_dict)

        reply = directory.get_reply_list(headers, results)

        self.assertTrue(CTICommand.CLASS in reply and reply[CTICommand.CLASS] == Directory.COMMAND_CLASS)
        self.assertTrue(Directory.HEADERS in reply and reply[Directory.HEADERS] == headers)
        self.assertTrue(CTICommand.REPLYID in reply and reply[CTICommand.REPLYID] == self._command_id)
        self.assertTrue(Directory.RESULT_LIST in reply and reply[Directory.RESULT_LIST] == results)
        self.assertTrue(Directory.STATUS in reply and reply[Directory.STATUS] == Directory.STATUS_OK)
