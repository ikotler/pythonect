import re
import ast
import _ast


# Local imports

import parser


def __expr_list_to_str(expr_list):

    if not expr_list[1:]:

        return expr_list[0][1]

    # `[['->', '1'], [None, '__builtins__.print_']]`

    return expr_list[0][1] + ' ' + expr_list[0][0] + ' ' + __expr_list_to_str(expr_list[1:])


def __scope(buffer):

    scope = []

    in_string = False

    for idx in xrange(0, len(buffer)):

        # ' ... ' , " .... "

        if in_string:

            if buffer[idx] == '\'' or buffer[idx] == '"':

                in_string = False

        # ....

        else:

            if buffer[idx] == '\'' or buffer[idx] == '"':

                in_string = True

                continue

            if buffer[idx] == '(' or buffer[idx] == '[':

                scope.append(idx)

            if buffer[idx] == ')' or buffer[idx] == ']':

                # Assume '[ ... ]'

                stmt_as_is = False

                if buffer[idx] == ')':

                    # NOTE: It is legal to write `(x=0)` in Python, e.g. `foobar = dict(foo="bar")`

                    stmt_as_is = True

                yield (scope.pop() + 1, idx, stmt_as_is)


# A recursive preprocessor

def preprocessor(buffer, stmt_as_is, tries=0):

    new_buffer = buffer

    # Preprocessing Algorithm:
    # ------------------------
    # For each *python* expression, return python expression
    # For each *python* statement, return python statement
    # For each item in [], preprocess item (recursive)
    # For each item in (), preprocess item (recursive)
    # For each function address, preprocess function_address, return __builtins__.remotefunction()

    ##########
    # PYTHON #
    ##########

    try:

        # Assume it's (a) Python and (b) statement

        type = 'PYTHON_STATEMENT'

        # Parse Python

        for node in ast.iter_child_nodes(ast.parse(buffer)):

            # Expression?

            if isinstance(node, _ast.Expr):

                # It's (a) Python and (b) expression

                type = 'PYTHON_EXPRESSION'

                new_buffer = buffer

            # Rewrite Python's `print` statement as an expression

            if isinstance(node, _ast.Print):

                new_buffer = '__builtins__.print_'

                # "Module(body=[Print(dest=None, values=[Str(s='Hello World')], nl=True)])"

                if node.values:

                    # i.e. "print_(...)"

                    new_buffer = '__builtins__.print_(\'' + node.values[0].s + '\')'

                # It's (a) Python and (b) expression

                type = 'PYTHON_EXPRESSION'

        # It was (a) Python and (b) statement

        if type == 'PYTHON_STATEMENT':

            if stmt_as_is:

                # AS IT IS

                new_buffer = buffer

            # Wrap in `__builtins__.stmt()`

            else:

                # Escape single quotes in buffer (e.g. stmt('q=[stmt('x = 0')]') => stmt('q=[stmt(\'x = 0\')]'))

                escaped_buffer = re.sub('\'', '\\\'', buffer)

                new_buffer = '__builtins__.stmt(\'' + escaped_buffer + '\')'

        return (type, new_buffer)

    #############
    # PYTHONECT #
    #############

    except Exception, e:

        # Maximum two passes

        if tries == 2:

            raise e

    # Multi items preprocessing

    for (start_idx, end_idx, scope_stmt_as_is) in __scope(new_buffer):

        tmp_buffer = ""

        new_array_content = []

        array_content = new_buffer[start_idx:end_idx]

        p = parser.Parser(scope_stmt_as_is)

        for item in p.parse(array_content):

            # Single item? it's Pythonect `expr` (i.e. Python expression or statement). Leave it as it.

            if len(item) == 1:

                new_array_content.append(item[0][1])

            # Multiple items? It's Pythonect `expr_list`. Conver it to string, and wrap it with `expr()`

            else:

                new_array_content.append('__builtins__.expr(\'' + __expr_list_to_str(item).rstrip() + '\')')

        # AS A CALL

        if (start_idx - 2) > -1 and new_buffer[start_idx - 2] == '$':

            # Convert `[expr('1 -> float')] to `[expr('1 -> float')(globals(), locals())]

            for expr in new_array_content:

                tmp_buffer = tmp_buffer + expr + '(globals(), locals()),'

            # Chop the trailing ',' tail

            tmp_buffer = tmp_buffer[:-1]

            # Expand `array_content` to include `$` for the upcoming Search & Replace

            array_content = new_buffer[start_idx - 2:end_idx + 1]

        # AS IT IS

        else:

            tmp_buffer = ','.join(new_array_content)

        # Search & Replace every `array_content` with `tmp_buffer`

        new_buffer = new_buffer.replace(array_content, tmp_buffer)

    # Preprocess function addresses

    for function_address in re.findall('.*\@.*', new_buffer):

        (fcn_name, fcn_host) = function_address.split('@')

        left_parenthesis = fcn_name.find('(')

        right_parenthesis = fcn_name.find(')')

        # foobar(1,2,3)@xmlrpc://...

        if left_parenthesis > -1 and right_parenthesis > -1:

            # `1,2,3`

            fcn_args = fcn_name[left_parenthesis + 1:right_parenthesis]

            # `foobar`

            fcn_name = fcn_name.split('(')[0]

            new_buffer = new_buffer.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\')(' + fcn_args + ')')

        # foobar@xmlrpc://...

        else:

            new_buffer = new_buffer.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\')')

    # Try again!

    return preprocessor(new_buffer, stmt_as_is, tries + 1)
