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

import unittest
import networkx


# Local imports

import pythonect.internal.parsers.p2y


class TestPythonectScriptParser(unittest.TestCase):

    def test_program_empty(self):

        g = networkx.DiGraph()

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('').nodes()) == len(g.nodes()), True)

    def test_expr_atom(self):

        g = networkx.DiGraph()

        g.add_node('1')

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('1').nodes()) == len(g.nodes()), True)

    def test_shebang_line_with_even_expr_atom_op_expr(self):

        g = networkx.DiGraph()

        g.add_node('1')

        g.add_node('2')

        g.add_edge('1', '2')

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('#! /usr/bin/env pythonect\n1 -> 1').edges()) == len(g.edges()), True)

    def test_even_expr_atom_op_expr(self):

        g = networkx.DiGraph()

        g.add_node('1')

        g.add_node('2')

        g.add_edge('1', '2')

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('1 -> 1').edges()) == len(g.edges()), True)

    def test_odd_expr_atom_op_expr(self):

        g = networkx.DiGraph()

        g.add_node('1')

        g.add_node('2')

        g.add_node('3')

        g.add_edge('1', '2')

        g.add_edge('2', '3')

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('1 -> 1 -> 1').edges()) == len(g.edges()), True)

    def test_program_expr_list(self):

        g = networkx.DiGraph()

        g.add_node('1')

        g.add_node('2')

        self.assertEqual(len(pythonect.internal.parsers.p2y.PythonectScriptParser().parse('1 , 2').nodes()) == len(g.nodes()), True)
