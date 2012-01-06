import unittest

from tests.mock import Mock

from xivo_cti.ami.actions.originate import Originate
from xivo_cti.cti.missing_field_exception import MissingFieldException


class Test(unittest.TestCase):

    def setUp(self):
        self._originate = Originate()
        self._originate.channel = 'SIP/123'
        self._originate.exten = '800'
        self._originate.context = 'default'
        self._originate.priority = 1

    def tearDown(self):
        pass

    def test_originate(self):
        originate = Originate()
        self.assertEqual(originate.action, 'Originate')
        self.assertEqual(originate.actionid, None)
        self.assertEqual(originate.channel, None)
        self.assertEqual(originate.exten, None)
        self.assertEqual(originate.context, None)
        self.assertEqual(originate.priority, None)
        self.assertEqual(originate.application, None)
        self.assertEqual(originate.data, None)
        self.assertEqual(originate.timeout, None)
        self.assertEqual(originate.callerid, None)
        self.assertEqual(originate.variable, None)
        self.assertEqual(originate.account, None)
        self.assertEqual(originate.async, None)
        self.assertEqual(originate.codecs, [])

    def test_check_required_fields(self):
        originate = Originate()
        self.assertTrue(originate._fields_missing())
        originate.channel = 'SIP/1234'
        self.assertTrue(originate._fields_missing())

    def test_optionnal_dependency_missing(self):
        originate = Originate()
        originate.channel = 'SIP/123'
        self.assertTrue(originate._optionnal_dependency_missing())
        originate.exten = '1234'
        originate.context = 'default'
        originate.priority = 1
        self.assertFalse(originate._optionnal_dependency_missing())
        del originate.priority
        self.assertTrue(originate._optionnal_dependency_missing())
        originate.application = 'MyApp'
        originate.data = 'mydata'
        self.assertFalse(originate._optionnal_dependency_missing())

    def test_get_arg(self):
        originate = Originate()
        try:
            originate._get_args()
            self.assertTrue(False, u'Should have raised an exception')
        except MissingFieldException:
            self.assertTrue(True, u'Should throw an exception')
        originate.channel = 'SIP/123456'
        originate.exten = '123'
        originate.context = 'default'
        originate.priority = 1
        args = originate._get_args()
        self.assertEqual(len(args), 4)
        self.assertTrue(('Exten', '123') in args)
        self.assertTrue(('Context', 'default') in args)
        self.assertTrue(('Priority', 1) in args)
        self.assertTrue(('Channel', 'SIP/123456') in args)

    def test_send(self):
        ami = Mock()
        ami.sendcommand = Mock()

        self._originate.send(ami)

        ami.sendcommand.assert_called_once_with('Originate',
                                                [('Channel', 'SIP/123'),
                                                 ('Exten', '800'),
                                                 ('Context', 'default'),
                                                 ('Priority', 1)])


if __name__ == "__main__":
    unittest.main()
