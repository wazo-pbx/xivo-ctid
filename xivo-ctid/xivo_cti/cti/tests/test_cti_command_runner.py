import unittest
from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_runner import CTICommandRunner


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_run_command(self):
        class TestCommand(CTICommand):
            _callbacks_with_params = []
            def __init__(self, color, shape):
                self.color = color
                self.shape = shape
            def get_description(self):
                return '%s %s' % (self.color, self.shape)
        class Handler(object):
            def handle_test(self, color, shape, description):
                self.color = color
                self.shape = shape
                self.description = description
        reply_ok = {"status": "OK"}
        handler = Handler()
        TestCommand.register_callback_params(handler.handle_test, ['color', 'shape', 'get_description'])
        color = 'blue'
        shape = 'circle'
        command = TestCommand(color, shape)

        runner = CTICommandRunner()

        reply = runner.run(command)

        self.assertEqual(handler.color, color)
        self.assertEqual(handler.shape, shape)
        self.assertEqual(handler.description, '%s %s' % (color, shape))
        self.assertEqual(reply, reply_ok)

    def test_run_command_typo(self):
        class TestCommand(CTICommand):
            _callbacks_with_params = []
        class Handler(object):
            def handle_test(self, color):
                pass
        handler = Handler()
        TestCommand.register_callback_params(handler.handle_test, ['typo'])

        command = TestCommand()

        runner = CTICommandRunner()

        self.assertRaises(AttributeError, lambda: runner.run(command))

    def test_run_replies(self):
        message_type = 'message'
        class TestCommand2(CTICommand):
            command_class = 'command_2'
            _callbacks_with_params = []
            def __init__(self, color):
                self.color = color
                self.commandid = 1234
            def get_description(self):
                return '%s %s' % (self.color)
        class Handler(object):
            def handle_test(self, color):
                return 'message', {'color': color}
        color = 'blue'
        reply_ok = {message_type: {'color': color}, 'replyid': 1234, 'class': TestCommand2.command_class}
        handler = Handler()
        TestCommand2.register_callback_params(handler.handle_test, ['color'])
        command = TestCommand2(color)

        runner = CTICommandRunner()

        reply = runner.run(command)

        self.assertEqual(reply, reply_ok)
