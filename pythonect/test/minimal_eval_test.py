#!/usr/bin/python

import unittest
import os
import sys

# Add `internal` directory (i.e. ../) to sys.path

sys.path.append(os.path.abspath('../'))


# Local imports

import eval


class TestPythonect(unittest.TestCase):
	
	def setUp(self):
		
		self.input = None
		
	def test_literal_hex(self):
		
		self.assertEqual( eval.eval('0x01', {}, {}) , 1 )
		
	def test_literal_bin(self):
		
		self.assertEqual( eval.eval('0b1', {}, {}) , 1 )
		
	def test_literal_float(self):
		
		self.assertEqual( eval.eval('1.0', {}, {}) , 1 )
		
	def test_literal_int(self):
		
		self.assertEqual( eval.eval('1', {}, {}) , 1 )
		
	def test_python_stmt_import(self):
		
		self.assertEqual( eval.eval('import math', {}, {}) , self.input )
		
	def test_python_stmt_assignment(self):
		
		self.assertEqual( eval.eval('x = 1', {}, {}) , self.input )
		
	def test_python_expr_int(self):
		
		self.assertEqual( eval.eval('1 + 1', {}, {}) , 2 )
		
	def test_python_expr_str(self):
		
		self.assertEqual( eval.eval('"Hello World"', {}, {}) , "Hello World" )
		
	def test_python_expr_list(self):
		
		self.assertEqual( eval.eval('[[1,2,3]]', {}, {}) , [1,2,3] )
		
	def test_python_true_expr_literal_eq_literal(self):
		
		self.assertEqual( eval.eval('1 == 1', {}, {}) , self.input )
		
	def test_python_false_expr_literal_neq_literal(self):
		
		self.assertEqual( eval.eval('1 == 0', {}, {}) , False )
		
	def test_python_true_expr_underscore_eq_underscore(self):
		
		self.assertEqual( eval.eval('_ == _', {}, {}) , self.input )
		
	def test_python_false_expr_underscore_neq_repr_underscore(self):
		
		self.assertEqual( eval.eval('_ == repr(_)', {}, {}) , False )
		
	def test_literal_int_async_none(self):
		
		self.assertEqual( eval.eval('1 -> None', {}, {}) , 1 )
		
	def test_literal_int_sync_none(self):
		
		self.assertEqual( eval.eval('1 | None', {}, {}) , 1 )
		
	def test_literal_int_async_literal_int(self):
		
		self.assertEqual( eval.eval('1 -> 1', {}, {}) , 1 )
		
	def test_literal_int_sync_literal_int(self):
		
		self.assertEqual( eval.eval('1 | 1', {}, {}) , 1 )
		
	def test_literal_int_async_literal_array_int_float(self):
		
		self.assertItemsEqual( eval.eval('1 -> [int,float]', {}, {}) , [1,1.0] )
		
	def test_literal_int_sync_literal_array_int_float(self):
		
		self.assertEqual( eval.eval('1 | [int,float]', {}, {}) , [1,1.0] )
		
	def test_python_stmt_assignment_async_literal_int(self):
		
		self.assertEqual( eval.eval('[ x = 0 ] -> 1', {}, {}) , 1 )
		
	def test_python_stmt_assignment_sync_literal_int(self):
		
		self.assertEqual( eval.eval('[ x = 0 ] | 1', {}, {}) , 1 )
		
	def test_python_stmt_assignment_sync_variable(self):
		
		self.assertEqual( eval.eval('[ x = 0 ] | x', {}, {}) , 0 )
		
	def test_python_stmt_assignment_async_variable(self):
		
		self.assertEqual( eval.eval('[ x = 0 ] -> x', {}, {}) , 0 )
		
	def test_literal_array_int_int_sync_none(self):
		
		self.assertEqual( eval.eval('[1,2] | None', {}, {}) , [1,2] )
		
	def test_literal_array_int_int_async_none(self):
		
		self.assertItemsEqual( eval.eval('[1,2] -> None', {}, {}) , [1,2] )
		
	def test_literal_array_int_str_async_none(self):
		
		self.assertItemsEqual( eval.eval('[1,"Hello"] -> None', {}, {}) , [1,"Hello"] )
		
	def test_literal_array_int_str_sync_none(self):
		
		self.assertEqual( eval.eval('[1, "Hello"] | None', {}, {}) , [1,"Hello"] )
		
	def test_literal_array_int_str_async_int(self):
		
		self.assertItemsEqual( eval.eval('[1,"Hello"] -> 1', {}, {}) , [1,1] )
		
	def test_literal_array_int_str_sync_int(self):
		
		self.assertEqual( eval.eval('[1, "Hello"] | 1', {}, {}) , [1,1] )
		
	def test_literal_array_int_int_sync_literal_int(self):
		
		self.assertEqual( eval.eval('[1,2] | 1', {}, {}) , [1,1] )
		
	def test_literal_array_int_int_async_literal_int(self):
		
		self.assertEqual( eval.eval('[1,2] -> 1', {}, {}) , [1,1] )
		
	def test_literal_array_int_int_sync_literal_array_int_int(self):
		
		self.assertEqual( eval.eval('[1,2] | [3,4]', {}, {}) , [3,4,3,4] )
		
	def test_literal_array_int_int_async_literal_array_int_int(self):
		
		self.assertItemsEqual( eval.eval('[1,2] -> [3,4]', {}, {}) , [3,3,4,4] )
		
	def test_literal_int_async_stmt_single_return_value_function_async_single_return_value_function(self):
		
		self.assertEqual( eval.eval('1 -> def foobar(x): return x+1 -> foobar', {}, {}) , 2 )
		
	def test_literal_int_async_stmt_single_return_value_function_sync_single_return_value_function(self):
		
		self.assertEqual( eval.eval('1 -> def foobar(x): return x+1 | foobar', {}, {}) , 2 )
		
	def test_literal_int_sync_stmt_single_return_value_function_async_single_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): return x+1 -> foobar', {}, {}) , 2 )
		
	def test_literal_int_sync_stmt_single_return_value_function_sync_single_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): return x+1 | foobar', {}, {}) , 2 )
		
	def test_literal_int_async_stmt_multiple_return_value_function_async_multiple_return_value_function(self):
		
		self.assertItemsEqual( eval.eval('1 -> def foobar(x): return [x,x+1] -> foobar', {}, {}) , [1,2] )
		
	def test_literal_int_async_stmt_multiple_return_value_function_sync_multiple_return_value_function(self):
		
		self.assertEqual( eval.eval('1 -> def foobar(x): return [x,x+1] | foobar', {}, {}) , [1,2] )
		
	def test_literal_int_sync_stmt_multiple_return_value_function_async_multiple_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): return [x,x+1] -> foobar', {}, {}) , [1,2] )
		
	def test_literal_int_sync_stmt_multiple_return_value_function_sync_multiple_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): return [x,x+1] | foobar', {}, {}) , [1,2] )
		
	def test_literal_int_async_stmt_generator_return_value_function_async_generator_return_value_function(self):
		
		self.assertItemsEqual( eval.eval('1 -> def foobar(x): yield x; yield x+1 -> foobar', {}, {}) , [1,2] )
		
	def test_literal_int_async_stmt_generator_return_value_function_sync_generator_return_value_function(self):
		
		self.assertEqual( eval.eval('1 -> def foobar(x): yield x; yield x+1 | foobar', {}, {}) , [1,2] )
		
	def test_literal_int_sync_stmt_generator_return_value_function_async_generator_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): yield x; yield x+1 -> foobar', {}, {}) , [1,2] )
		
	def test_literal_int_sync_stmt_generator_return_value_function_sync_generator_return_value_function(self):
		
		self.assertEqual( eval.eval('1 | def foobar(x): yield x; yield x+1 | foobar', {}, {}) , [1,2] )
		
