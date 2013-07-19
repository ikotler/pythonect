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

import networkx
import tokenize
import StringIO
import re


# Local imports

import pythonect.internal.parsers
import pythonect.internal._graph


def _create_and_link(graph, new_node_name, new_node_kwargs):

    # Add Node

    graph.add_node(new_node_name, **new_node_kwargs)

    # Connect Any Tail Nodes to Node

    for tail_node in [node for node, degree in graph.out_degree().items() if degree == 0 and node != new_node_name]:

        graph.add_edge(tail_node, new_node_name)


def _make_graph(code, node_prefix='', depth=0, in_brackets=False):

    meaningful_graph = False

    update_tail_nodes_operator = False

    create_node = False

    node_value = ""

    edge_value = ""

    previous_tokval = None

    in_literal_scope = 0

    graph = pythonect.internal._graph.Graph()

    tokens = tokenize.generate_tokens(StringIO.StringIO(code).readline)

    token_pos = -1

    seek = 0

    in_statement = False

    in_url = False

    graphs = []

    for toknum, tokval, (srow, scol), (erow, ecol), line in tokens:

        extra_string = ''

        # print "[Row %d, Col %d]: Received (#%d) %s" % (srow, scol, toknum, tokval)

        # Skip over INDENT/NL

        if toknum in [tokenize.INDENT, tokenize.NL, tokenize.NEWLINE, tokenize.DEDENT]:

            continue

        token_pos = token_pos + 1

        # Fast Forward

        if seek > 0:

            seek = seek - 1

            continue

        if not in_url and ((toknum == tokenize.NAME and tokval != '_') or tokval == ':'):

            extra_string = ' '

        node_value = node_value + tokval + extra_string

        # Within '(....)' or '{...}' ?

        if in_literal_scope:

            if tokval in ')}' or in_statement and tokval in ']':

                in_literal_scope = in_literal_scope - 1

            # i.e. ({ ... })

            if tokval in '({' or in_statement and tokval in '[':

                in_literal_scope = in_literal_scope + 1

            continue

        # Start of '@xmlrpc://...' ?

        if tokval == '@':

            in_url = True

            continue

        # Not Within '@xmlrpc://...' ...

        if not in_url:

            # Start of Python Statement Scope?

            if tokval in [':', '=']:

                in_statement = True

                continue

            # Start of '(...)' or '{...}' ?

            if tokval in '({' or in_statement and tokval in '[':

                in_literal_scope = in_literal_scope + 1

                continue

        # '->' Operator?

        if tokval == '>' and previous_tokval == '-':

            meaningful_graph = True

            in_statement = False

            in_url = False

            edge_value = '->'

            # Trim trailing '->'

            node_value = node_value[:-2]

            if node_value:

                create_node = True

            else:

                update_tail_nodes_operator = True

        # '|' Operator?

        if tokval == '|':

            meaningful_graph = True

            in_url = False

            in_statement = False

            edge_value = '|'

            # Trim trailing '|'

            node_value = node_value[:-1]

            if node_value:

                create_node = True

            else:

                update_tail_nodes_operator = True

        # New Node?

        if create_node:

            create_node = False

            _create_and_link(graph, node_prefix + str(len(graphs)) + "." + str(len(graph.nodes())), {'CONTENT': node_value, 'OPERATOR': edge_value, 'TOKEN_TYPE': tokval})

            node_value = ""

        # Update Tail Node(s) Operator? (i.e. [ A , B ] -> C ; -> is of 'A' and 'B')

        if update_tail_nodes_operator:

            update_tail_nodes_operator = False

            for tail_node in [node for node, degree in graph.out_degree().items() if degree == 0]:

                graph.node[tail_node].update({'OPERATOR': edge_value})

        # Start of '[...]'

        if node_value == tokval == '[':

            # Supress '['

            node_value = node_value[:-1]

            # Start New Graph

            (next_token_pos, ret_graph) = _make_graph(code[scol + 1:], node_prefix + str(len(graphs)) + "." + str(len(graph.nodes())) + '.', depth + 1, True)

            # ['1 2 3'.split()]

            if len(ret_graph.nodes()) == 1 and ret_graph.node[ret_graph.nodes()[0]]['CONTENT'].find('(') != -1:

                # AS IS

                node_value = '[' + ret_graph.node[ret_graph.nodes()[0]]['CONTENT'] + ']'

            # [1], [string.split], or [1, 2, 3, ..]

            else:

                in_nodes = [node for node, degree in ret_graph.in_degree().items() if degree == 0]

                out_nodes = [node for node, degree in graph.out_degree().items() if degree == 0]

                graph = networkx.union(graph, ret_graph)

                for in_node in in_nodes:

                    for out_node in out_nodes:

                        graph.add_edge(out_node, in_node)

            seek = next_token_pos

        if tokval == ']' and in_brackets:

            in_brackets = False

            # Trim trailing ']'

            node_value = node_value[:-1]

            if not meaningful_graph and not node_value:

                node_value = '[[' + ','.join([graph.node[node]['CONTENT'] for node in sorted(graph.nodes())]) + ']]'

                graph.clear()

            # Flush node_value

            if node_value:

                _create_and_link(graph, node_prefix + str(len(graphs)) + "." + str(len(graph.nodes())), {'CONTENT': node_value, 'TOKEN_TYPE': tokval})

                node_value = ""

            # Merge graphs? (i.e. [ A -> B , C -> D ])

            if graphs:

                graphs = [graph] + graphs

                graph = reduce(networkx.union, graphs)

            # End Graph

            return (token_pos + 1, graph)

        if tokval == ',':

            meaningful_graph = True

            # Flush node_value

            # Trim trailing ','

            node_value = node_value[:-1]

            _create_and_link(graph, node_prefix + str(len(graphs)) + "." + str(len(graph.nodes())), {'CONTENT': node_value, 'TOKEN_TYPE': tokval})

            node_value = ""

            # Replace graph

            graphs.append(graph)

            # New graph

            graph = pythonect.internal._graph.Graph()

        previous_tokval = tokval

    # EOF

    if node_value:

        _create_and_link(graph, node_prefix + str(len(graphs)) + "." + str(len(graph.nodes())), {'CONTENT': node_value, 'TOKEN_TYPE': tokval})

        node_value = ""

    # Merge graphs? (i.e. [ A -> B , C -> D ])

    if graphs:

        graphs = [graph] + graphs

        graph = reduce(networkx.union, graphs)

    # End Graph

    return (token_pos + 1, graph)


class PythonectScriptParser(pythonect.internal.parsers.PythonectInputFileFormatParser):

    def parse(self, source):

        graph = None

        try:

            (ignored_ret, graph) = _make_graph(re.sub('#.*', '', source.strip()))

        except tokenize.TokenError:

            pass

        return graph

    FILE_EXTS = ['p2y']
