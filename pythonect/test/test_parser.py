#!/usr/bin/python

import unittest
import os
import sys


# Local imports

import pythonect


class TestPythonectParser(unittest.TestCase):

    def test_program_empty(self):

        self.assertEqual(pythonect.parse(''), [])

    def test_expr_atom(self):

        self.assertEqual(pythonect.parse('1'), [[[None, '1']]])

    def test_even_expr_atom_op_expr(self):

        self.assertEqual(pythonect.parse('1 -> 1'), [[['->', '1'], [None, '1']]])

    def test_odd_expr_atom_op_expr(self):

        self.assertEqual(pythonect.parse('1 -> 1 -> 1'), [[['->', '1'], ['->', '1'], [None, '1']]])

    def test_program_expr_list(self):

        self.assertEqual(pythonect.parse('1 , 2'), [[[None, '1']], [[None, '2']]])
