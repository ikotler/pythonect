# Copyright (c) 2012-2013, Itzik Kotler
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:

    # If < Python 2.7, use the backported unittest2 package

    import unittest2 as unittest

except ImportError:

    # Probably > Python 2.7, use unittest

    import unittest


import os
import sys
import copy


# Local imports

import pythonect


def _not_python27():

    major, minor = sys.version_info[:2]

    return not (major > 2 or (major == 2 and minor >= 7))


def _installed_module(name):

    try:

        __import__(name)

        return True

    except ImportError:

        return False


class TestPythonect(unittest.TestCase):

    def setUp(self):

        self.input = None

        self.locals_ = {'__MAX_THREADS_PER_FLOW__': 2}

        self.globals_ = {'__MAX_THREADS_PER_FLOW__': 2}

    def test_literal_hex(self):

        self.assertEqual(pythonect.eval('0x01', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_sub_expr_literal_hex(self):

        self.assertEqual(pythonect.eval('`0x01`', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_bin(self):

        self.assertEqual(pythonect.eval('0b1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_float(self):

        self.assertEqual(pythonect.eval('1.0', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_int(self):

        self.assertEqual(pythonect.eval('1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_python_stmt_import(self):

        self.assertEqual(pythonect.eval('import math', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_sub_expr_python_stmt_import(self):

        self.assertEqual(pythonect.eval('`import math`', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_python_stmt_assignment(self):

        self.assertEqual(pythonect.eval('x = 1', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_sub_expr_python_stmt_assignment(self):

        self.assertEqual(pythonect.eval('`x = 1`', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_python_expr_int(self):

        self.assertEqual(pythonect.eval('1 + 1', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_sub_expr_python_expr_int(self):

        self.assertEqual(pythonect.eval('`1 + 1`', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_python_expr_str_1(self):

        self.assertEqual(pythonect.eval('"Hello World"', copy.copy(self.globals_), copy.copy(self.locals_)), "Hello World")

    def test_sub_expr_python_expr_str_1(self):

        self.assertEqual(pythonect.eval('`"Hello World"`', copy.copy(self.globals_), copy.copy(self.locals_)), "Hello World")

    def test_python_expr_str_2(self):

        self.assertEqual(pythonect.eval("'Hello World'", copy.copy(self.globals_), copy.copy(self.locals_)), "Hello World")

    def test_python_expr_str_3(self):

        self.assertEqual(pythonect.eval('"Hello \'W\'orld"', copy.copy(self.globals_), copy.copy(self.locals_)), "Hello 'W'orld")

    def test_python_expr_str_4(self):

        self.assertEqual(pythonect.eval("'Hello \"W\"orld'", copy.copy(self.globals_), copy.copy(self.locals_)), 'Hello "W"orld')

    def test_python_expr_list(self):

        self.assertEqual(pythonect.eval('[[1, 2, 3]]', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2, 3])

#   TODO: Supported in Pythonect < 0.6 ; is worth maintaining in Pythonect 0.6+?
#
#    def test_sub_expr_python_expr_list(self):
#
#       self.assertEqual(pythonect.eval('`[[1, 2, 3]]`', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2, 3])

    def test_python_true_expr_literal_eq_literal(self):

        self.assertEqual(pythonect.eval('1 == 1', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_sub_expr_python_true_expr_literal_eq_literal(self):

        self.assertEqual(pythonect.eval('`1 == 1`', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_python_false_expr_literal_neq_literal(self):

        self.assertEqual(pythonect.eval('1 == 0', copy.copy(self.globals_), copy.copy(self.locals_)), False)

    def test_python_true_expr_underscore_eq_underscore(self):

        self.assertEqual(pythonect.eval('_ == _', copy.copy(self.globals_), copy.copy(self.locals_)), self.input)

    def test_python_false_expr_underscore_neq_repr_underscore(self):

        self.assertEqual(pythonect.eval('_ == repr(_)', copy.copy(self.globals_), copy.copy(self.locals_)), False)

    def test_literal_int_async_none(self):

        self.assertEqual(pythonect.eval('1 -> None', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_int_sync_none(self):

        self.assertEqual(pythonect.eval('1 | None', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_int_async_dict(self):

        self.assertEqual(pythonect.eval('1 -> {1: "One", 2: "Two"}', copy.copy(self.globals_), copy.copy(self.locals_)), "One")

    def test_literal_int_sync_dict(self):

        self.assertEqual(pythonect.eval('1 | {1: "One", 2: "Two"}', copy.copy(self.globals_), copy.copy(self.locals_)), "One")

    def test_literal_str_async_autoload(self):

        self.assertEqual(pythonect.eval('"Hello world" -> string.split', copy.copy(self.globals_), copy.copy(self.locals_)), ["Hello", "world"])

    def test_literal_str_sync_autoload(self):

        self.assertItemsEqual(pythonect.eval('"Hello world" | string.split', copy.copy(self.globals_), copy.copy(self.locals_)), ["Hello", "world"])

    def test_literal_int_async_literal_int(self):

        self.assertEqual(pythonect.eval('1 -> 1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_int_sync_literal_int(self):

        self.assertEqual(pythonect.eval('1 | 1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_literal_int_async_literal_array_int_float(self):

        self.assertItemsEqual(pythonect.eval('1 -> [int,float]', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1.0])

    def test_literal_int_sync_literal_array_int_float(self):

        self.assertEqual(pythonect.eval('1 | [int,float]', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1.0])

    def test_python_stmt_assignment_async_literal_int(self):

        self.assertEqual(pythonect.eval('[x = 0] -> 1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_python_stmt_assignment_sync_literal_int(self):

        self.assertEqual(pythonect.eval('[x = 0] | 1', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_python_stmt_assignment_sync_variable(self):

        self.assertEqual(pythonect.eval('[x = 0] | x', copy.copy(self.globals_), copy.copy(self.locals_)), 0)

    def test_python_stmt_assignment_async_variable(self):

        self.assertEqual(pythonect.eval('[x = 0] -> x', copy.copy(self.globals_), copy.copy(self.locals_)), 0)

    def test_literal_array_int_int_sync_none(self):

        self.assertEqual(pythonect.eval('[1, 2] | None', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_array_int_int_async_none(self):

        self.assertItemsEqual(pythonect.eval('[1, 2] -> None', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_array_int_int_sync_dict(self):

        self.assertEqual(pythonect.eval('[1, 2] | {1: "One", 2: "Two"}', copy.copy(self.globals_), copy.copy(self.locals_)), ["One", "Two"])

    def test_literal_array_int_int_async_dict(self):

        self.assertItemsEqual(pythonect.eval('[1, 2] -> {1: "One", 2: "Two"}', copy.copy(self.globals_), copy.copy(self.locals_)), ["One", "Two"])

    def test_literal_array_int_str_async_none(self):

        self.assertItemsEqual(pythonect.eval('[1, "Hello"] -> None', copy.copy(self.globals_), copy.copy(self.locals_)), [1, "Hello"])

    def test_literal_array_int_str_sync_none(self):

        self.assertEqual(pythonect.eval('[1, "Hello"] | None', copy.copy(self.globals_), copy.copy(self.locals_)), [1, "Hello"])

    def test_literal_array_int_str_async_int(self):

        self.assertItemsEqual(pythonect.eval('[1, "Hello"] -> 1', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1])

    def test_literal_array_int_str_sync_int(self):

        self.assertEqual(pythonect.eval('[1, "Hello"] | 1', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1])

    def test_literal_array_int_int_sync_literal_int(self):

        self.assertEqual(pythonect.eval('[1, 2] | 1', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1])

    def test_literal_array_int_int_async_literal_int(self):

        self.assertEqual(pythonect.eval('[1, 2] -> 1', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 1])

    def test_literal_array_int_int_sync_literal_array_int_int(self):

        self.assertEqual(pythonect.eval('[1, 2] | [3, 4]', copy.copy(self.globals_), copy.copy(self.locals_)), [3, 4, 3, 4])

    def test_literal_array_int_int_async_literal_array_int_int(self):

        self.assertItemsEqual(pythonect.eval('[1, 2] -> [3, 4]', copy.copy(self.globals_), copy.copy(self.locals_)), [3, 3, 4, 4])

    def test_literal_int_async_stmt_single_return_value_function_async_single_return_value_function(self):

        self.assertEqual(pythonect.eval('1 -> def foobar(x): return x+1 -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_literal_int_async_stmt_single_return_value_function_sync_single_return_value_function(self):

        self.assertEqual(pythonect.eval('1 -> def foobar(x): return x+1 | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_literal_int_sync_stmt_single_return_value_function_async_single_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): return x+1 -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_literal_int_sync_stmt_single_return_value_function_sync_single_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): return x+1 | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_literal_int_async_stmt_multiple_return_value_function_async_multiple_return_value_function(self):

        self.assertItemsEqual(pythonect.eval('1 -> def foobar(x): return [x,x+1] -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_async_stmt_multiple_return_value_function_sync_multiple_return_value_function(self):

        self.assertEqual(pythonect.eval('1 -> def foobar(x): return [x,x+1] | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_sync_stmt_multiple_return_value_function_async_multiple_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): return [x,x+1] -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_sync_stmt_multiple_return_value_function_sync_multiple_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): return [x,x+1] | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_async_stmt_generator_return_value_function_async_generator_return_value_function(self):

        self.assertItemsEqual(pythonect.eval('1 -> def foobar(x): yield x; yield x+1 -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_async_stmt_generator_return_value_function_sync_generator_return_value_function(self):

        self.assertEqual(pythonect.eval('1 -> def foobar(x): yield x; yield x+1 | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_sync_stmt_generator_return_value_function_async_generator_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): yield x; yield x+1 -> foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_literal_int_sync_stmt_generator_return_value_function_sync_generator_return_value_function(self):

        self.assertEqual(pythonect.eval('1 | def foobar(x): yield x; yield x+1 | foobar', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2])

    def test_singlethread_program_async(self):

        self.assertEqual(pythonect.eval('import threading -> x = threading.current_thread().name -> y = threading.current_thread().name -> x == y', copy.copy(self.globals_), copy.copy(self.locals_)), None)

    def test_singlethread_program_sync(self):

        self.assertEqual(pythonect.eval('import threading | x = threading.current_thread().name | y = threading.current_thread().name | x == y', copy.copy(self.globals_), copy.copy(self.locals_)), None)

    def test_multithread_program_async(self):

        r_array = pythonect.eval('import threading -> [threading.current_thread().name, threading.current_thread().name]', copy.copy(self.globals_), copy.copy(self.locals_))

        self.assertEqual(r_array[0] != r_array[1], True)

    def test_multithread_program_sync(self):

        r_array = pythonect.eval('import threading | [threading.current_thread().name, threading.current_thread().name]', copy.copy(self.globals_), copy.copy(self.locals_))

        self.assertEqual(r_array[0] != r_array[1], True)

    @unittest.skipIf(_not_python27(), 'Current Python implementation does not support multiprocessing (buggy)')
    def test_multiprocess_program_async(self):

        r_array = pythonect.eval('import threading -> [multiprocessing.current_process().pid &, multiprocessing.current_process().pid &]', copy.copy(self.globals_), copy.copy(self.locals_))

        self.assertEqual(r_array[0] != r_array[1], True)

#        self.assertEqual(pythonect.eval('import multiprocessing -> start_pid = multiprocessing.current_process().pid -> start_pid -> str & -> current_pid = multiprocessing.current_process().pid -> 1 -> current_pid != start_pid', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    @unittest.skipIf(_not_python27(), 'Current Python implementation does not support multiprocessing (buggy)')
    def test_multiprocess_program_sync(self):

        r_array = pythonect.eval('import multiprocessing | [multiprocessing.current_process().pid &, multiprocessing.current_process().pid &]', copy.copy(self.globals_), copy.copy(self.locals_))

        self.assertEqual(r_array[0] != r_array[1], True)

#        self.assertEqual(pythonect.eval('import multiprocessing | start_pid = multiprocessing.current_process().pid | start_pid | str & | current_pid = multiprocessing.current_process().pid | 1 | current_pid != start_pid', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_pseudo_none_const_as_url(self):

        self.assertEqual(pythonect.eval('def foobar(x): return x+1 -> 1 -> foobar@None', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_pseudo_none_str_as_url(self):

        self.assertEqual(pythonect.eval('def foobar(x): return x+1 -> 1 -> foobar@"None"', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_pseudo_none_value_fcn_return_value_as_url(self):

        self.assertEqual(pythonect.eval('def ret_none(): return None -> def foobar(x): return x+1 -> 1 -> foobar@ret_none()', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_pseudo_none_str_fcn_return_value_as_url(self):

        self.assertEqual(pythonect.eval('def ret_none(): return "None" -> def foobar(x): return x+1 -> 1 -> foobar@ret_none()', copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    def test_pythonect_eval_fcn(self):

        self.assertEqual(pythonect.eval("eval('1->1', {'__MAX_THREADS_PER_FLOW__': 2}, {'__MAX_THREADS_PER_FLOW__': 2})", copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_python_eval_within_pythonect_program(self):

        self.assertEqual(pythonect.eval("__eval__('1')", copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_void_function(self):

        self.assertEqual(pythonect.eval("def void_foobar(): return 2 -> 1 -> void_foobar", copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    ############################################################
    # Ticket numbers in this file can be looked up by visiting #
    # http://github.com/ikotler/pythonect/issues/<number>      #
    ############################################################

    # Bug #11

    def test_autloader_within_array(self):

        self.assertItemsEqual(pythonect.eval('"Hello world" | [string.split]', copy.copy(self.globals_), copy.copy(self.locals_)), ["Hello", "world"])

    # Bug #14

    def test_print_like_statement(self):

        self.assertItemsEqual(pythonect.eval('range(1,10) -> print("Thread A")', copy.copy(self.globals_), copy.copy(self.locals_)), [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_multiple_stateful_x_eq_5_statement(self):

        locals_ = copy.copy(self.locals_)

        globals_ = copy.copy(self.globals_)

        pythonect.eval('xrange(1, 10) -> x = _', globals_, locals_)

        self.assertEqual('x' not in locals_ and 'x' not in globals_, True)

        # i.e.

        # >>> xrange(x, 10) -> x = _
        # >>> x
        # NameError: name 'x' is not defined

    def test_stateful_x_eq_5_statement(self):

        locals_ = copy.copy(self.locals_)

        globals_ = copy.copy(self.globals_)

        pythonect.eval('x = 5', globals_, locals_)

        self.assertEqual(pythonect.eval('1 -> [x == 5]', globals_, locals_), 1)

        # i.e.

        # >>> x = 5
        # >>> 1 -> [x == 5]
        # 1

    # Bug #16

    def test_typeerror_exception_not_due_to_eval(self):

        with self.assertRaisesRegexp(TypeError, 'takes exactly'):

            pythonect.eval('1 -> socket.socket(socket.AF_INET, socket.SOCK_STREAM) -> _.connect("A","B")', copy.copy(self.globals_), copy.copy(self.locals_))

    # Bug #21

    def test_list_with_str_with_comma(self):

        self.assertEqual(pythonect.eval('["Hello, world"]', copy.copy(self.globals_), copy.copy(self.locals_)), 'Hello, world')

    # Bug #27

#    @unittest.skipIf(not _installed_module('multiprocessing'), 'Current Python implementation does not support multiprocessing')
#    def test_multi_processing_and_multi_threading(self):
#
#        try:
#
#            self.assertEqual(pythonect.eval('"Hello, world" -> [print, print &]', copy.copy(self.globals_), copy.copy(self.locals_)), ['Hello, world', 'Hello, world'])
#
#        except OSError as e:
#
#            # i.e. OSError: [Errno 13] Permission denied
#
#            return 1

    # Bug #30

    def test_non_string_literals_in_list(self):

        self.assertEqual(pythonect.eval('[1,2,3] -> _ + 1', copy.copy(self.globals_), copy.copy(self.locals_)), [2, 3, 4])

    # Feature #35

    def test_eval_with_expressions_list_as_input(self):

        expressions = pythonect.parse('"Hello, world" -> 1 | 2')

        self.assertEqual(pythonect.eval(expressions, copy.copy(self.globals_), copy.copy(self.locals_)), 2)

    # Enhancement #45

    def test_literal_dict_as_input(self):

        self.assertEqual(pythonect.eval('{"foobar": "foobar"}', copy.copy(self.globals_), copy.copy(self.locals_)), {"foobar": "foobar"})

    def test_dict_as_return_value_as_input(self):

        self.assertEqual(pythonect.eval("def foobar(): return {'foobar': 'foobar'} -> foobar() -> print", copy.copy(self.globals_), copy.copy(self.locals_)), {"foobar": "foobar"})

    # Bug #48

    def test_print_B_in_ABC(self):

        self.assertEqual(pythonect.eval('1 -> print "B" in "ABC"', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    def test_print_2_is_2(self):

        self.assertEqual(pythonect.eval('1 -> print 2 is 2', copy.copy(self.globals_), copy.copy(self.locals_)), 1)

    # Bug #69

    def test_alt_print__fcn(self):

        self.assertEqual(pythonect.eval('1 -> print', copy.copy(self.globals_), {'print_': lambda x: 123}), 123)

    # Feature 70 (Freeze on Python 2.6 and Mac OS X Python 2.7.2)
    #
    #def test_max_threads_eq_0(self):
    #
    #    with self.assertRaisesRegexp(ValueError, 'Number of processes must be at least'):
    #
    #        pythonect.eval('range(1, 3) -> _+1', copy.copy(self.globals_), {'__MAX_THREADS_PER_FLOW__': 0})
