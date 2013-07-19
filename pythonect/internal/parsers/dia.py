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
import xml.sax
import gzip
import StringIO


# Local imports

import pythonect.internal.parsers
import pythonect.internal._graph


# Tested on dia-bin 0.97.2

class _DiaParser(xml.sax.handler.ContentHandler):

    def __init__(self):

        xml.sax.handler.ContentHandler.__init__(self)

        self._in_dia_object = False

        self._in_dia_string = False

        self.node_name = None

        self.edge = []

        self.node_value = {'OPERATOR': '->'}

    def startElement(self, name, attrs):

        if self._in_dia_object:

            if name == 'dia:string':

                self._in_dia_string = True

            if name == 'dia:connection':

                self.edge.append(attrs['to'])

                if len(self.edge) == 2:

                    self._graph.add_edge(self.edge[0], self.edge[1])

                    self.edge = []

        else:

            if name == 'dia:object':

                if self._graph is None:

                    self._graph = pythonect.internal._graph.Graph()

                self._in_dia_object = True

                self.node_name = attrs['id']

                self._graph.add_node(self.node_name)

    def endElement(self, name):

        if name == 'dia:object':

            self._graph.node[self.node_name].update(self.node_value)

            if self._graph.node[self.node_name].get('CONTENT', None) is None:

                self._graph.remove_node(self.node_name)

            self.node_name = None

            self.node_value = {'OPERATOR': '->'}

            self._in_dia_object = False

        if name == 'dia:string':

            self._in_dia_string = False

    def characters(self, content):

        if self._in_dia_string:

            # Strip leading and trailing '#'

            self.node_value.update({'CONTENT': content[1:-1]})

    def endDocument(self):

        if self._graph is None:

            self._graph = pythonect.internal._graph.Graph()

    def parse(self, source):

        self._graph = None

        try:

            # Compressed?

            try:

                # UTF-8?

                try:

                    source = source.encode('utf-8')

                except UnicodeDecodeError:

                    pass

                source = gzip.GzipFile(fileobj=StringIO.StringIO(source), mode='rb').read()

            except IOError:

                pass

            xml.sax.parseString(source, self)

            # Delete 'OPERATOR' from tail nodes

            tail_nodes = [node for node, degree in self._graph.out_degree().items() if degree == 0]

            for node in tail_nodes:

                del self._graph.node[node]['OPERATOR']

        except xml.sax._exceptions.SAXParseException:

            pass

        return self._graph


class PythonectDiaParser(pythonect.internal.parsers.PythonectInputFileFormatParser):

    def parse(self, source):

        graph = _DiaParser().parse(source)

        return graph

    FILE_EXTS = ['dia']
