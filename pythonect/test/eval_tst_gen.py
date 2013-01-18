#!/usr/bin/env python
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

import sys
import os


# Add `internal` directory (i.e. ../) to sys.path

sys.path.append(os.path.abspath('../'))


# Local imports

import internal.eval


ATOM = [
    ('literal_underscore', '_'),
    ('literal_true_expr', '1 == 1'),
    ('literal_false_expr', '1 != 1'),
    ('literal_int', '1'),
    ('literal_float', '0.5'),
    ('literal_string', '\"foobar\"'),
    ('literal_true', 'True'),
    ('literal_false', 'False'),
    ('literal_none', 'None'),
    ('import_stmt', 'import math'),
    ('assignment_stmt', 'x = 0'),
    ('python_expr', '1+1'),
    ('pythonect_expr', '$[1->1]')
]


OPERATOR = [
    (None, None),
    ('comma', ','),
    ('async', '->'),
    ('sync', '|')
]


# ATOM OPERATOR ATOM OPERATOR ATOM

MAX_DEPTH = 5


def __type_wrapper(data):

    if isinstance(data, str):

        return '\'%s\'' % (data)

    return data


def pythonect_expr_generator(name=[], expr=[], depth=0):

    for (type, value) in ATOM:

        name.append(type)

        expr.append(value)

        # ATOM AND OPERATOR

        if (depth + 2 < MAX_DEPTH):

            for (type, value) in OPERATOR:

                if type is None:

                    yield (name, expr)

                    continue

                name.append(type)

                expr.append(value)

                for (return_type, return_value) in pythonect_expr_generator([], [], depth + 2):

                    yield(name + return_type, expr + return_value)

                name.pop()

                expr.pop()

        # ATOM

        else:

            yield (name, expr)

        name.pop()

        expr.pop()


def main():

    for (name, expr) in pythonect_expr_generator():

        try:

            print '\tdef test_%s(self):\n\n\t\tself.assertEqual( internal.eval.eval(\'%s\', {}, {}) , %s )\n' % \
                ('_'.join(name), ' '.join(expr), __type_wrapper(internal.eval.eval(' '.join(expr), {}, {})))

        except Exception as e:

            print "%s raises Exception %s" % (' '.join(expr), str(e))

if __name__ == "__main__":

    sys.exit(main())
