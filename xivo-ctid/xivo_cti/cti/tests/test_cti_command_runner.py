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
            def __init__(self, color, shape):
                self.color = color
                self.shape = shape
            def get_description(self):
                return '%s %s' % (self.color, self.shape)
        class Handler(object):
            def handle_test(self, color, shape, description):
                self.color = color
                self.shape= shape
                self.description = description
        handler = Handler()
        TestCommand.register_callback_params(handler.handle_test, ['color', 'shape', 'get_description'])
        color = 'blue'
        shape = 'circle'
        command = TestCommand(color, shape)

        runner = CTICommandRunner()

        runner.run(command)

        self.assertEqual(handler.color, color)
        self.assertEqual(handler.shape, shape)
        self.assertEqual(handler.description, '%s %s' % (color, shape))

    def test_run_command_typo(self):
        class TestCommand(CTICommand):
            pass
        class Handler(object):
            def handle_test(self, color):
                pass
        handler = Handler()
        TestCommand.register_callback_params(handler.handle_test, ['typo'])

        command = TestCommand()

        runner = CTICommandRunner()

        self.assertRaises(AttributeError, lambda: runner.run(command))

