import re
import ast
import _ast
import codegen


# Local imports

import parser


SUB_EXPRESSION = re.compile("`(?P<sub_expr>.*)`")


def __expr_list_to_str(expr_list):

    if not expr_list[1:]:

        return expr_list[0][1]

    # `[['->', '1'], [None, '__builtins__.print_']]`

    return expr_list[0][1] + ' ' + expr_list[0][0] + ' ' + __expr_list_to_str(expr_list[1:])


def __split(buffer):

    new_buffer = []

    depth = 0

    points = []

    in_str = False

    for idx in xrange(0, len(buffer)):

        char = buffer[idx]

        if char == '[' or char == '(' or char == '{':

            depth = depth + 1

        if char == ']' or char == ')' or char == '}':

            depth = depth - 1

        if char == '"' or char == "'":

            if in_str:

                depth = depth - 1

            else:

                depth = depth + 1

        if char == ',' and depth == 0:

            points.append(idx)

    if not points:

        # One item

        new_buffer.append(buffer)

    else:

        last_point = -1

        # Multiple items

        for point in points:

            new_buffer.append(buffer[last_point + 1:point])

            last_point = point

        # Last item

        new_buffer.append(buffer[point + 1:])

    return new_buffer


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

    # Preprocessing Algorithm:
    # ------------------------
    # For each `` replace with __builtins__.expr()
    # For each *python* expression, return python expression
    # For each *python* statement, return python statement
    # For each item in [], preprocess item (recursive)
    # For each item in (), preprocess item (recursive)
    # For each function address, preprocess function_address, return __builtins__.remotefunction()
    # For each trailing &, return __builtins__.attributedcode()

    # `ABC` to __builtins__.expr('ABC')

    buffer = SUB_EXPRESSION.sub("__builtins__.expr(\'\g<sub_expr>\')(globals(), locals())", buffer)

    new_buffer = buffer

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

                # Is value is List or Tuple?

                if isinstance(node.value, _ast.List) or isinstance(node.value, _ast.Tuple):

                    # TODO: This is a hack, should be reimplemented

                    array_content = []

                    for item in __split(buffer[1:-1]):

                        item_node = ast.parse(item).body[0].value

                        # Is item *NOT* a literal, and not already wrapped (i.e. Pythonect statement)?

                        if (isinstance(item_node, _ast.Call) or isinstance(item_node, _ast.Attribute) or isinstance(item_node, _ast.Name)) and not item.startswith('__builtins__'):

                                array_content.append('__builtins__.expr(\'' + re.sub('\'', '\\\'', item) + '\')')

                        # Is item literal?

                        else:

                            array_content.append(item)

                    if isinstance(node.value, _ast.List):

                        new_buffer = '[' + ','.join(array_content) + ']'

                    if isinstance(node.value, _ast.Tuple):

                        new_buffer = '(' + ','.join(array_content) + ')'

            # Rewrite Python's `print` statement as an expression

            if isinstance(node, _ast.Print):

                new_buffer = '__builtins__.print_'

                # "Module(body=[Print(dest=None, values=[Str(s='Hello World')], nl=True)])"

                if node.values:

                    new_buffer = '__builtins__.print_(' + codegen.to_source(node)[5:] + ')'

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

    except SyntaxError:

        # Maximum two passes

        if tries == 2:

            # AS IT IS (Assume it's expression)

            return ('PYTHON_EXPRESSION', buffer)

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

            new_buffer = new_buffer.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\',' + fcn_args + ')')

        # foobar@xmlrpc://...

        else:

            new_buffer = new_buffer.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\')')

    # Change Provider to Process?

    if new_buffer.rstrip()[-1] == '&':

        new_buffer = new_buffer.rstrip()[:-1]

        actual_buffer = preprocessor(new_buffer, stmt_as_is, tries)

        # Assume new_buffer is from PYTHON_EXPRESSION

        try:

            import multiprocessing

            new_buffer = '__builtins__.attributedcode("(operator, \'%s\')", "(iterate_literal_arrays, multiprocessing.Process, multiprocessing.Queue)")' % actual_buffer[1]

        except ImportError:

            # Don't break syntax due to missing multiprocessing, use Threads if applicable.

            pass

    # Try again!

    return preprocessor(new_buffer, stmt_as_is, tries + 1)
