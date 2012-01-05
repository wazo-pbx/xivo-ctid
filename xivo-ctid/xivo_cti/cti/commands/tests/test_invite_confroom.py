import unittest

from xivo_cti.cti.missing_field_exception import MissingFieldException
from xivo_cti.cti.commands.invite_confroom import InviteConfroom


class Test(unittest.TestCase):

    def setUp(self):
        self._command_class = 'invite_confroom'

    def tearDown(self):
        pass

    def test_invite_confroom(self):
        self.assertEqual(len(InviteConfroom.required_fields), 2)
        self.assertTrue('class' in InviteConfroom.required_fields)
        self.assertTrue('invitee' in InviteConfroom.required_fields)

        try:
            InviteConfroom({'class': self._command_class})
            self.assertTrue(False, u'Should raise an exception')
        except MissingFieldException:
            self.assertTrue(True, u'Should raise an exception')

        invitee = 'user:myxivo/123'
        command = InviteConfroom({'class': self._command_class, 'invitee': invitee})
        self.assertEqual(command._command_class, self._command_class)
        self.assertEqual(command._invitee, invitee)

    def test_match_message(self):
        self.assertFalse(InviteConfroom.match_message({}))
        self.assertFalse(InviteConfroom.match_message({'class': 'invite_confroom*'}))
        self.assertTrue(InviteConfroom.match_message({'class': 'invite_confroom'}))

if __name__ == "__main__":
    unittest.main()
