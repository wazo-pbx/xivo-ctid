import unittest

from mock import Mock
from xivo_cti import cti_sheets
from xivo_cti.innerdata import Channel

class TestSheets(unittest.TestCase):

    def setUp(self):
        self.title = 'My Test Sheet Title'
        self.field_type = 'text'
        self.default_value = 'my_default_value'
        self.format_string = '{xivo-test}'
        self.disabled = 0
        self.var_value = 'my_test_var_content'

        self.line_properties = [self.title,
                                self.field_type,
                                self.default_value,
                                self.format_string,
                                self.disabled]

        self.sheet = cti_sheets.Sheet(None, None, None)
        self.sheet.channelprops = Mock(Channel)
        self.sheet.channelprops.channel = 'mychannel'
        self.sheet.channelprops.unique_id = 12345
    
    def test_split_format_string(self):
        format_string = '{xivo-var}'

        family, var = cti_sheets.split_format_string(format_string)

        self.assertEqual(family, 'xivo')
        self.assertEqual(var, 'var')

    def test_split_format_string_invalid(self):
        format_string = 'xivo-var'
        self.assertRaises(ValueError,
                          lambda: cti_sheets.split_format_string(format_string))

        format_string = '{xivo/var}'
        self.assertRaises(ValueError,
                          lambda: cti_sheets.split_format_string(format_string))

    def test_resolv_line_content(self):
        self.sheet.channelprops.extra_data = {'xivo':
                                                  {'test': self.var_value}}
        expected = {'name': self.title,
                    'type': self.field_type,
                    'contents': self.var_value}
 
        result = self.sheet.resolv_line_content(self.line_properties)

        self.assertEquals(result, expected)

    def test_resolv_line_content_default(self):
        self.sheet.channelprops.extra_data = {}
        expected = {'name': self.title,
                    'type': self.field_type,
                    'contents': self.default_value}

        result = self.sheet.resolv_line_content(self.line_properties)

        self.assertEquals(result, expected)
        
    def test_resolv_line_content_callerpicture(self):
        user_id = '6'
        encoded_picture = 'my picture base 64 encoding'
        self.sheet.channelprops.extra_data = {'xivo': {'userid': user_id}}
        self.sheet._get_user_picture = Mock(return_value=encoded_picture)
        expected = {'name': self.title,
                    'type': self.field_type,
                    'contents': encoded_picture}

        result = self.sheet.resolv_line_content([self.title,
                                                 self.field_type,
                                                 self.default_value,
                                                 '{xivo-callerpicture}'])
        self.sheet._get_user_picture.assert_called_once_with(user_id)

        self.assertEquals(result, expected)
