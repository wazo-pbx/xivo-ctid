import unittest
from xivo_cti.tools import weak_method


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_weakref_function(self):
        def func(arg):
            return arg * 2
        f = weak_method.WeakCallable(func)
        self.assertEqual(f(1234), 2468)
        del func
        try:
            f(1234)
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)

    def test_weakref_method(self):
        class Test(object):
            def func(self, arg):
                return arg * 2
        instance = Test()
        f = weak_method.WeakCallable(instance.func)
        self.assertEqual(f(1234), 2468)
        del instance
        try:
            f(1234)
            self.assertTrue(False)
        except TypeError:
            self.assertTrue(True)

    def test_method_dead(self):
        class Test(object):
            def func(self, arg):
                return arg * 2
        instance = Test()
        f = weak_method.WeakCallable(instance.func)
        self.assertFalse(f.dead())
        del instance
        self.assertTrue(f.dead())

    def test_function_dead(self):
        def func(arg):
            return arg * 2
        f = weak_method.WeakCallable(func)
        self.assertFalse(f.dead())
        del func
        self.assertTrue(f.dead())
