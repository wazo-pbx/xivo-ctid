# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.exception import InvalidCallbackException
from xivo_cti.tools import weak_method
from xivo_cti.tools.weak_method import WeakMethodBound, WeakMethodFree


class TestWeakref(unittest.TestCase):

    def test_weakref_function(self):
        def func(arg):
            return arg * 2
        f = weak_method.WeakCallable(func)
        self.assertEqual(f(1234), 2468)
        del func
        self.assertRaises(InvalidCallbackException, f, 1234)

    def test_weakref_method(self):
        class Test(object):
            def func(self, arg):
                return arg * 2
        instance = Test()
        f = weak_method.WeakCallable(instance.func)
        self.assertEqual(f(1234), 2468)
        del instance
        self.assertRaises(InvalidCallbackException, f, 1234)

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

    def test_weak_method_equal_other_type(self):
        def func1(param):
            pass

        class TestClass(object):
            def func1(self):
                pass

        instance = TestClass()

        def func2(param):
            pass

        ref1_free = WeakMethodFree(func1)
        ref1_bound = WeakMethodBound(instance.func1)
        ref2 = func2

        self.assertNotEqual(ref1_free, ref2)
        self.assertNotEqual(ref1_bound, ref2)

    def test_call_dead_weak_method_bound(self):
        class TestClass:
            def func(self):
                pass
        instance = TestClass()
        ref = WeakMethodBound(instance.func)
        del instance

        self.assertRaises(InvalidCallbackException, ref)

    def test_call_dead_function(self):
        def func():
            pass
        ref = WeakMethodFree(func)
        del func

        self.assertRaises(InvalidCallbackException, ref)
