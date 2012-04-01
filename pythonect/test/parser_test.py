#!/usr/bin/python

import unittest
import os
import sys


# Add `internal` directory (i.e. ../) to sys.path

sys.path.append(os.path.abspath('../'))


# Local imports

import internal.parser


class TestPythonectParser(unittest.TestCase):
	
	def setUp(self):
		
		self.parser = internal.parser.Parser()
		
	def test_program_empty(self):
		
		self.assertEqual( self.parser.parse(''), [] )
		
	def test_expr_atom(self):
		
		self.assertEqual( self.parser.parse('1') , [[[None, '1']]] )
		
	def test_even_expr_atom_op_expr(self):
		
		self.assertEqual( self.parser.parse('1 -> 1'), [[['->', '1'], [None, '1']]] )
		
	def test_odd_expr_atom_op_expr(self):
		
		self.assertEqual( self.parser.parse('1 -> 1 -> 1') , [[['->', '1'], ['->', '1'], [None, '1']]] )
		
	def test_program_expr_list(self):
		
		self.assertEqual( self.parser.parse('1 , 2') , [[[None, '1']], [[None, '2']]] )
		
