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

import __builtin__ as python
import threading
import copy
import logging
import importlib
import site
import os
import multiprocessing
import multiprocessing.dummy
import multiprocessing.pool
import pickle
import networkx
import re
import pprint


# Local imports

import parsers
import lang
import _graph


# Consts

SUB_EXPRESSION = re.compile("`(?P<sub_expr>.*)`")


# Global variables

global_interpreter_lock = threading.Lock()


# Classes

class _PythonectResult(object):

    def __init__(self, values):

        self.values = values


class _PythonectLazyRunner(object):

    def __init__(self, node):

        self.node = node

    def go(self, graph, reduces):

        reduced_value = []

        # TODO: Merge dicts and not pick the 1st one

        locals_ = reduces[self.node][0]['locals']

        globals_ = reduces[self.node][0]['globals']

        for values in reduces[self.node]:

            reduced_value.append(values['last_value'])

        locals_['_'] = globals_['_'] = reduced_value

        return _run(graph, self.node, globals_, locals_, {'as_reduce': True}, None, False)


# Functions

def __isiter(object):

    try:

        iter(object)

        return True

    except TypeError:

        return False


def __pickle_safe_dict(locals_or_globals):

    result = dict(locals_or_globals)

    for k, v in locals_or_globals.iteritems():

        try:

            # NOTE: Is there a better/faster way?

            pickle.dump(v, open(os.devnull, 'w'))

        except Exception:

            del result[k]

    return result


def __create_pool(globals_, locals_):

    return multiprocessing.dummy.Pool(locals_.get('__MAX_THREADS_PER_FLOW__', multiprocessing.cpu_count() + 1))


def __resolve_and_merge_results(results_list):

    resolved = []

    try:

        for element in results_list:

            if isinstance(element, multiprocessing.pool.ApplyResult):

                element = element.get()

            if isinstance(element, list):

                for sub_element in element:

                    resolved.append(sub_element)

            else:

                resolved.append(element)

    except TypeError:

        resolved = results_list

    return resolved


def _run_next_virtual_nodes(graph, node, globals_, locals_, flags, pool, result):

    operator = graph.node[node].get('OPERATOR', None)

    return_value = []

    not_safe_to_iter = False

    is_head_result = True

    head_result = None

    # "Hello, world" or {...}

    if isinstance(result, (basestring, dict)) or not __isiter(result):

        not_safe_to_iter = True

    # [[1]]

    if isinstance(result, list) and len(result) == 1 and isinstance(result[0], list):

        result = result[0]

        not_safe_to_iter = True

    # More nodes ahead?

    if operator:

        if not_safe_to_iter:

            logging.debug('not_safe_to_iter is True for %s' % result)

            head_result = result

            tmp_globals = copy.copy(globals_)

            tmp_locals = copy.copy(locals_)

            tmp_globals['_'] = tmp_locals['_'] = head_result

            return_value = __resolve_and_merge_results(_run(graph, node, tmp_globals, tmp_locals, {}, None, True))

        else:

            # Originally this was implemented using result[0] and result[1:] but xrange() is not slice-able, thus, I have changed it to `for` with buffer for 1st result

            for res_value in result:

                logging.debug('Now at %s from %s' % (res_value, result))

                if is_head_result:

                    logging.debug('is_head_result is True for %s' % res_value)

                    is_head_result = False

                    head_result = res_value

                    tmp_globals = copy.copy(globals_)

                    tmp_locals = copy.copy(locals_)

                    tmp_globals['_'] = tmp_locals['_'] = head_result

                    return_value.insert(0, _run(graph, node, tmp_globals, tmp_locals, {}, None, True))

                    continue

                tmp_globals = copy.copy(globals_)

                tmp_locals = copy.copy(locals_)

                tmp_globals['_'] = tmp_locals['_'] = res_value

                # Synchronous

                if operator == '|':

                    return_value.append(pool.apply(_run, args=(graph, node, tmp_globals, tmp_locals, {}, None, True)))

                # Asynchronous

                if operator == '->':

                    return_value.append(pool.apply_async(_run, args=(graph, node, tmp_globals, tmp_locals, {}, None, True)))

            pool.close()

            pool.join()

            pool.terminate()

            logging.debug('return_value = %s' % return_value)

            return_value = __resolve_and_merge_results(return_value)

    # Loopback

    else:

        # AS IS

        if not_safe_to_iter:

            return_value = [result]

        # Iterate for all possible *return values*

        else:

            for res_value in result:

                return_value.append(res_value)

            # Unbox

            if len(return_value) == 1:

                return_value = return_value[0]

    return return_value


def __import_module_from_exception(exception, globals_):

    # NameError: name 'os' is not defined
    #  - OR -
    # NameError: global name 'os' is not defined

    mod_name = exception.message[exception.message.index("'") + 1:exception.message.rindex("'")]

    globals_.update({mod_name: importlib.import_module(mod_name)})


def __pythonect_preprocessor(current_value):

    current_value = current_value.strip()

    flags = {'spawn_as_process': False, 'spawn_as_reduce': False}

    # foobar(_!)

    if current_value.find('_!') != -1:

        current_value = current_value.replace('_!', '_')

        flags['spawn_as_reduce'] = True

    # foobar &

    if current_value.endswith('&'):

        current_value = current_value[:-1].strip()

        flags['spawn_as_process'] = True

    # foobar@xmlrpc://...

    for function_address in re.findall('.*\@.*', current_value):

        (fcn_name, fcn_host) = function_address.split('@')

        left_parenthesis = fcn_name.find('(')

        right_parenthesis = fcn_name.find(')')

        # foobar(1,2,3)@xmlrpc://...

        if left_parenthesis > -1 and right_parenthesis > -1:

            # `1,2,3`

            fcn_args = fcn_name[left_parenthesis + 1:right_parenthesis]

            # `foobar`

            fcn_name = fcn_name.split('(')[0]

            current_value = current_value.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\',' + fcn_args + ')')

        # foobar@xmlrpc://...

        else:

            current_value = current_value.replace(function_address, '__builtins__.remotefunction(\'' + fcn_name + '\',\'' + fcn_host + '\')')

    # foobar(`1 -> _+1`)

    current_value = SUB_EXPRESSION.sub("__builtins__.expr(\'\g<sub_expr>\')(globals(), locals())", current_value)

    # Replace `print` with `print_`

    if current_value == 'print':

        current_value = 'print_'

    if current_value.startswith('print'):

        current_value = 'print_(' + current_value[5:] + ')'

    return current_value, flags


def __node_main(current_value, last_value, globals_, locals_):

    logging.info('In __node_main, current_value = %s, last_value = %s' % (current_value, last_value))

    return_value = None

    try:

        ###################################
        # Try to eval()uate current_value #
        ###################################

        try:

            return_value = python.eval(current_value, globals_, locals_)

        # Autoloader Try & Catch

        except NameError as e:

            try:

                __import_module_from_exception(e, globals_)

                return_value = python.eval(current_value, globals_, locals_)

            except Exception as e1:

                raise e1

        # Current value is already Python Object

        except TypeError as e:

            # Due to eval()?

            if (e.message == 'eval() arg 1 must be a string or code object'):

                return_value = current_value

            else:

                raise e

        ##########################
        # eval() Post Processing #
        ##########################

        if isinstance(return_value, lang.remotefunction):

            return_value.evaluate_host(globals_, locals_)

        if isinstance(return_value, dict):

            if last_value is not None:

                return_value = return_value.get(last_value, False)

        if return_value is None or (isinstance(return_value, bool) and return_value is True):

            return_value = last_value

        if callable(return_value):

            # Ignore "copyright", "credits", "license", and "help"

            if isinstance(return_value, (site._Printer, site._Helper)):

                return_value = return_value()

            else:

                try:

                    return_value = return_value(last_value)

                except TypeError as e:

                    if e.args[0].find('takes no arguments') != -1:

                        return_value = return_value()

                    else:

                        raise e

                if return_value is None:

                    return_value = last_value

    except SyntaxError as e:

        ##################################
        # Try to exec()ute current_value #
        ##################################

        try:

            exec current_value in globals_, locals_

        # Autoloader Try & Catch

        except NameError as e:

            try:

                __import_module_from_exception(e, globals_)

                exec current_value in globals_, locals_

            except Exception as e1:

                raise e1

        return_value = last_value

    return return_value


def _run_next_graph_nodes(graph, node, globals_, locals_, pool):

    operator = graph.node[node].get('OPERATOR', None)

    nodes_return_value = []

    return_value = None

    # False? Terminate Flow.

    if isinstance(locals_['_'], bool) and locals_['_'] is False:

        return False

    if operator:

        #   -->  (a)
        #   --> / | \
        #    (b) (c) (d)
        #       \ | /
        #        (e)

        next_nodes = sorted(graph.successors(node))

        # N-1

        for next_node in next_nodes[1:]:

            # Synchronous

            if operator == '|':

                nodes_return_value.append(pool.apply(_run, args=(graph, next_node, globals_, locals_, {}, None, False)))

            # Asynchronous

            if operator == '->':

                nodes_return_value.append(pool.apply_async(_run, args=(graph, next_node, globals_, locals_, {}, None, False)))

        # 1

        nodes_return_value.insert(0, _run(graph, next_nodes[0], globals_, locals_, {}, None, False))

        pool.close()

        pool.join()

        pool.terminate()

        return_value = __resolve_and_merge_results(nodes_return_value)

    else:

        #        (a)
        #       / | \
        #    (b) (c) (d)
        #       \ | /
        #    --> (e)

        return_value = locals_['_']

    return return_value


def __apply_current(func, args=(), kwds={}):

    return func(*args, **kwds)


def _run(graph, node, globals_, locals_, flags, pool=None, is_virtual_node=False):

    return_value = None

    if not pool:

        pool = __create_pool(globals_, locals_)

    if is_virtual_node:

        #   `[1,2,3] -> print`
        #
        #       =
        #
        #   ([1,2,3])
        #       |
        #    (print)
        #
        #       =
        #
        #   ([1,2,3])
        #   /   |   \
        #  {1} {2} {3} <-- virtual node
        #   \   |   /
        #    (print)

        # Call original `node` successors with `_` set as `virtual_node_value`

        return_value = _run_next_graph_nodes(graph, node, globals_, locals_, pool)

    else:

        #   `[1,2,3] -> print`
        #
        #       =
        #
        #   ([1,2,3])
        #       |
        #    (print)
        #
        #       =
        #
        #   ([1,2,3]) <-- node
        #   /   |   \
        #  {1} {2} {3}
        #   \   |   /
        #    (print)

        current_value = graph.node[node]['CONTENT']

        last_value = globals_.get('_', locals_.get('_', None))

        runner = __apply_current

        input_value = None

        code_flags = {}

        # Code or Literal?

        if not current_value.startswith('"') and not current_value.startswith("'") and not current_value[0] in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:

            # Preprocess Code

            try:

                logging.debug('Before __pythonect_preprocessor, value = %s' % current_value)

                input_value, code_flags = __pythonect_preprocessor(current_value)

                logging.debug('After __pythonect_preprocessor, value = %s' % input_value)

            except:

                # AS IS (Already Python Object)

                input_value = current_value

            # Run as Reduce?

            if code_flags.get('spawn_as_reduce', False) and flags.get('as_reduce', False) is False:

                return _PythonectResult({'node': node, 'input_value': input_value, 'last_value': last_value, 'locals': locals_, 'globals': globals_})

            # Run as a New Process?

            if code_flags.get('spawn_as_process', False):

                runner = multiprocessing.Pool(1).apply

                globals_ = __pickle_safe_dict(globals_)

                locals_ = __pickle_safe_dict(locals_)

        else:

            # Literal

            input_value = current_value

        # Run Code

        result = runner(__node_main, args=(input_value, last_value, globals_, locals_))

        # Call self with each result value as `virtual_node`

        return_value = _run_next_virtual_nodes(graph, node, globals_, locals_, flags, pool, result)

    return return_value


def __extend_builtins(globals_):

    # TODO: Is there any advantage to manually duplicate __builtins__, instead of passing our own?

    globals_['__builtins__'] = python

    # Add `pythonect.lang` to Python's `__builtins__`

    for name in dir(lang):

        # i.e. __builtins__.print_ = pythonect.lang.print_

        setattr(globals_['__builtins__'], name, getattr(lang, name))

    # Add GIL

    setattr(globals_['__builtins__'], '__GIL__', global_interpreter_lock)

    # Fix "copyright", "credits", and "license"

    setattr(globals_['__builtins__'], 'copyright', site._Printer("copyright", "Copyright (c) 2012-2013 by Itzik Kotler and others.\nAll Rights Reserved."))
    setattr(globals_['__builtins__'], 'credits', site._Printer("credits", "See www.pythonect.org for more information."))
    setattr(globals_['__builtins__'], 'license', site._Printer("license", "See https://github.com/ikotler/pythonect/blob/master/LICENSE", ["LICENSE"], [os.path.abspath(__file__ + "/../../../")]))

    # Map eval() to Pythonect's eval, and __eval__ to Python's eval

    globals_['__eval__'] = getattr(globals_['__builtins__'], 'eval')
    globals_['eval'] = eval

    # Default `iterate_literal_arrays`

    if not '__ITERATE_LITERAL_ARRAYS__' in globals_:

        globals_['__ITERATE_LITERAL_ARRAYS__'] = True

    return globals_


def _is_referencing_underscore(graph, node):

    if graph.node[node]['CONTENT'] == '_':

        return True

    return False


def parse(source):
    """Parse the source into a directed graph (i.e. networkx.DiGraph)

    Args:
        source: A string representing a Pythonect code.

    Returns:
        A directed graph (i.e. networkx.DiGraph) of Pythonect symbols.

    Raises:
        SyntaxError: An error occurred parsing the code.
    """

    graph = _graph.Graph()

    for ext, parser in parsers.get_parsers(os.path.abspath(os.path.join(os.path.dirname(parsers.__file__), '..', 'parsers'))).items():

        logging.debug('Trying to parse %s with %s' % (source, parser))

        tmp_graph = parser.parse(source)

        if tmp_graph is not None:

            logging.debug('Parsed successfully with %s, total nodes = %d' % (parser, len(tmp_graph.nodes())))

            if len(tmp_graph.nodes()) > len(graph.nodes()):

                graph = tmp_graph

    logging.info('Parsed graph contains %d nodes' % len(graph.nodes()))

    return graph


def eval(source, globals_={}, locals_={}):
    """Evaluate Pythonect code in the context of globals and locals.

    Args:
        source: A string representing a Pythonect code or a networkx.DiGraph() as
            returned by parse()
        globals: A dictionary.
        locals: Any mapping.

    Returns:
        The return value is the result of the evaluated code.

    Raises:
        SyntaxError: An error occurred parsing the code.
    """

    return_value = None

    # Meaningful program?

    if source != "pass":

        logging.info('Program is meaningful')

        return_value = []

        return_values = []

        globals_values = []

        locals_values = []

        tasks = []

        reduces = {}

        logging.debug('Evaluating %s with globals_ = %s and locals_ %s' % (source, globals_, locals_))

        if not isinstance(source, networkx.DiGraph):

            logging.info('Parsing program...')

            graph = parse(source)

        else:

            logging.info('Program is already parsed! Using source AS IS')

            graph = source

        root_nodes = sorted([node for node, degree in graph.in_degree().items() if degree == 0])

        if not root_nodes:

            cycles = networkx.simple_cycles(graph)

            if cycles:

                logging.info('Found cycles: %s in graph, using nodes() 1st node (i.e. %s) as root node' % (cycles, graph.nodes()[0]))

                root_nodes = [graph.nodes()[0]]

        logging.info('There are %d root node(s)' % len(root_nodes))

        logging.debug('Root node(s) are: %s' % root_nodes)

        # Extend Python's __builtin__ with Pythonect's `lang`

        start_globals_ = __extend_builtins(globals_)

        logging.debug('Initial globals_:\n%s' % pprint.pformat(start_globals_))

        # Default input

        start_globals_['_'] = start_globals_.get('_', locals_.get('_', None))

        logging.info('_ equal %s', start_globals_['_'])

        # Execute Pythonect program

        pool = __create_pool(globals_, locals_)

        # N-1

        for root_node in root_nodes[1:]:

            if globals_.get('__IN_EVAL__', None) is None and not _is_referencing_underscore(graph, root_node):

                # Reset '_'

                globals_['_'] = locals_['_'] = None

            if globals_.get('__IN_EVAL__', None) is None:

                globals_['__IN_EVAL__'] = True

            temp_globals_ = copy.copy(globals_)

            temp_locals_ = copy.copy(locals_)

            task_result = pool.apply_async(_run, args=(graph, root_node, temp_globals_, temp_locals_, {}, None, False))

            tasks.append((task_result, temp_locals_, temp_globals_))

        # 1

        if globals_.get('__IN_EVAL__', None) is None and not _is_referencing_underscore(graph, root_nodes[0]):

            # Reset '_'

            globals_['_'] = locals_['_'] = None

        if globals_.get('__IN_EVAL__', None) is None:

            globals_['__IN_EVAL__'] = True

        result = _run(graph, root_nodes[0], globals_, locals_, {}, None, False)

        # 1

        for expr_return_value in result:

            globals_values.append(globals_)

            locals_values.append(locals_)

            return_values.append([expr_return_value])

        # N-1

        for (task_result, task_locals_, task_globals_) in tasks:

            return_values.append(task_result.get())

            locals_values.append(task_locals_)

            globals_values.append(task_globals_)

        # Reduce + _PythonectResult Grouping

        for item in return_values:

            # Is there _PythonectResult in item list?

            for sub_item in item:

                if isinstance(sub_item, _PythonectResult):

                    # 1st Time?

                    if sub_item.values['node'] not in reduces:

                        reduces[sub_item.values['node']] = []

                        # Add Place holder to mark the position in the return value list

                        return_value.append(_PythonectLazyRunner(sub_item.values['node']))

                    reduces[sub_item.values['node']] = reduces[sub_item.values['node']] + [sub_item.values]

                else:

                    return_value.append(sub_item)

        # Any _PythonectLazyRunner's?

        if reduces:

            for return_item_idx in xrange(0, len(return_value)):

                if isinstance(return_value[return_item_idx], _PythonectLazyRunner):

                    # Swap list[X] with list[X.go(reduces)]

                    return_value[return_item_idx] = pool.apply_async(return_value[return_item_idx].go, args=(graph, reduces))

            return_value = __resolve_and_merge_results(return_value)

        # [...] ?

        if return_value:

            # Single return value? (e.g. [1])

            if len(return_value) == 1:

                return_value = return_value[0]

            # Update globals_ and locals_

#            globals_, locals_ = __merge_all_globals_and_locals(globals_, locals_, globals_values, {}, locals_values, {})

        # Set `return value` as `_`

        globals_['_'] = locals_['_'] = return_value

        if globals_.get('__IN_EVAL__', None) is not None:

            del globals_['__IN_EVAL__']

        pool.close()

        pool.join()

        pool.terminate()

    return return_value
