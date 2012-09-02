#!/usr/bin/env python

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
