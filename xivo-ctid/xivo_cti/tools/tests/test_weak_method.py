import unittest
from xivo_cti.tools import weak_method
from xivo_cti.tools.weak_method import WeakMethodBound, WeakMethodFree


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

    def test_weak_method_bound_equal(self):
        class TestClass(object):
            def func1(self):
                pass

            def func2(self):
                pass

        instance = TestClass()

        ref1 = WeakMethodBound(instance.func1)
        ref2 = WeakMethodBound(instance.func1)
        ref3 = WeakMethodBound(instance.func2)

        self.assertEqual(ref1, ref2)

        self.assertNotEqual(ref1, ref3)

    def test_weak_method_free_equal(self):
        def func1(param):
            pass

        def func2(param):
            pass

        ref1 = WeakMethodFree(func1)
        ref2 = WeakMethodFree(func1)
        ref3 = WeakMethodFree(func2)

        self.assertEqual(ref1, ref2)

        self.assertNotEqual(ref1, ref3)

    def test_call_dead_weak_method_bound(self):
        class TestClass:
            def func():
                pass
        instance = TestClass()
        ref = WeakMethodBound(instance.func)
        del instance

        self.assertRaises(TypeError, ref)

    def test_call_dead_function(self):
        def func():
            pass
        ref = WeakMethodFree(func)
        del func

        self.assertRaises(TypeError, ref)
