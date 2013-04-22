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
import types
import time
import site
import os
import sys
import multiprocessing
import multiprocessing.dummy
import multiprocessing.pool
import functools
import pickle


# Local imports

import parser
import lang


# Global variables

global_interpreter_lock = threading.Lock()


class NoDaemonProcess(multiprocessing.Process):

    # make 'daemon' attribute always return False
    def _get_daemon(self):

        return False

    def _set_daemon(self, value):

        pass

    daemon = property(_get_daemon, _set_daemon)


class NoDaemonPool(multiprocessing.pool.Pool):

    Process = NoDaemonProcess


def __isiter(object):

    try:

        iter(object)

        return True

    except TypeError as e:

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


def __create_default_pool(globals_, locals_):

    return multiprocessing.dummy.Pool(locals_.get('__MAX_THREADS_PER_FLOW__', multiprocessing.cpu_count() + 1))


def __create_pool(globals_, locals_):

    # Process Pool?

    if '__PROCESS__' in globals_ or '__PROCESS__' in locals_:

        return NoDaemonPool(locals_.get('__MAX_PROCESSES_PER_FLOW__', None))

    return __create_default_pool(globals_, locals_)


def __resolve_and_fix_results(results_list):

    resolved = []

    for element in results_list:

        if isinstance(element, multiprocessing.pool.ApplyResult):

            element = element.get()

        if isinstance(element, list):

            for sub_element in element:

                resolved.append(sub_element)

        else:

            resolved.append(element)

    return resolved


def __eval_current_atom(atom, locals_, globals_):

    # TODO: This is a hack to support instances, should be re-written. If atom is `literal` or `instance`, it should appear as a metadata/attribute

    try:

        object_or_objects = python.eval(atom, globals_, locals_)

    except NameError as e:

        try:

            import importlib

            # NameError: name 'os' is not defined
            #  - OR -
            # NameError: global name 'os' is not defined

            mod_name = e.message[e.message.index("'") + 1:e.message.rindex("'")]

            globals_.update({mod_name: importlib.import_module(mod_name)})

            object_or_objects = python.eval(atom, globals_, locals_)

        except Exception as e1:

            raise e1

    except TypeError as e:

        # Due to eval()?

        if (e.message == 'eval() arg 1 must be a string or code object'):

            object_or_objects = atom

        else:

            raise e

    return object_or_objects


def __fix_str_form(item):
    '''
    [1, 'Hello'] -> eval() = [1, Hello] , this fixup Hello to be 'Hello' again
    '''
    if isinstance(item, basestring):

        item = "'''" + item.replace("'", "\\'") + "'''"

    return item


def __run_resource_in_multi(operator, item, provider, expression, locals_, globals_):

    globals_.update({'__ITERATE_LITERAL_ARRAYS__': not globals_['__ITERATE_LITERAL_ARRAYS__']})

    # Synchronous

    if operator == '|':

        return provider.apply(eval, args=([[(operator, item)] + expression[1:]], globals_, locals_))

    # Asynchronous

    else:

        return provider.apply_async(eval, args=([[(operator, item)] + expression[1:]], globals_, locals_))


def __change_provider_in_multi(item, expression, operator, globals_, locals_):

    (new_globals_, new_locals_) = python.eval(item.get_attributes())

    # Update

    globals_.update(new_globals_)

    locals_.update(new_locals_)

    # Unpack __builtins.__attributedcode()

    expression = [(None, None), python.eval(item.get_expression())] + expression[1:]

    # Overwrite `item` with current input

    item = __fix_str_form(locals_.get('_', None))

    return (item, expression, __create_pool(globals_, locals_))


def __eval_multiple_objects(objects, operator, provider, expression, locals_, globals_):
    '''
    When objects is an appropriate iterable, it has handled as following:
    [1,2,3] -> [a,b,c] =
    Thread 1: 1 -> [a,b,c]
    Thread 2: 2 -> [a,b,c]
    ...
    '''

    return_value = []

    globals_values = []

    locals_values = []

    for item in objects:

        # TODO: This is a hack to prevent from item to be confused as fcn call and raise NameError.

        item = __fix_str_form(item)

        temp_globals_ = copy.copy(globals_)

        temp_locals_ = copy.copy(locals_)

        # Process? (i.e. 'Hello, world' -> [print, print &])

        if isinstance(item, lang.attributedcode):

            item, expression, provider = __change_provider_in_multi(item, expression, operator, globals_, locals_)

            temp_locals_ = __pickle_safe_dict(locals_)

            temp_globals_ = __pickle_safe_dict(globals_)

        if not isinstance(provider, multiprocessing.pool.ThreadPool):

            temp_globals_ = __pickle_safe_dict(copy.copy(globals_))

            temp_locals_ = __pickle_safe_dict(copy.copy(locals_))

        return_value.append(__run_resource_in_multi(operator, item, provider, expression, temp_locals_, temp_globals_))

        locals_values.append(temp_locals_)

        globals_values.append(temp_globals_)

    # Finally, join all asynchronous resources (outside the objects loop)

    provider.close()

    provider.join()

    # Resolve AsyncResult

    return_value = __resolve_and_fix_results(return_value)

#    if return_value and len(return_value) == 2 and isinstance(return_value[0], list) and isinstance(return_value[1], list):
#
#        # Convert [[(1, {}, {})], [(2, {}, {})]] to [(1, {}, {}), (2, {}, {})]
#
#        return reduce(lambda x, y: x + y, return_value)

    if len(globals_values) != 1:

        delta_globals_, delta_locals_ = __merge_all_globals_and_locals(globals_values[0], locals_values[0], globals_values[1:], {}, locals_values[1:], {})

        locals_.clear()
        globals_.clear()

        locals_.update(delta_locals_)
        globals_.update(delta_globals_)

    else:

        globals_, locals_ = temp_globals_, temp_locals_

    return return_value


def __apply_output_to_input(output, input_, locals_, globals_):

    # Remote?

    if isinstance(output, lang.remotefunction):

        output.evaluate_host(globals_, locals_)

    # Python Statement?

    if isinstance(output, (lang.stmt, lang.expr)):

        output = output(globals_, locals_)

    else:

        # Ignore "copyright", "credits", "license", and "help"

        if isinstance(output, (site._Printer, site._Helper)):

            output = output()

        else:

            try:

                output = output(input_)

            except TypeError as e:

                # i.e. TypeError: f() takes no arguments (1 given)

                if e.args[0].find('takes no arguments') != -1:

                    output = output()

                else:

                    raise e

    return output


def __handle_special_outputs(output, locals_, globals_, ignore_iterables):
    '''
    If 'output' is a function, apply it to '_' (the result of the last calculation).
    If 'output' is a dictionary - use it as a switch.
    If 'output' is True or None - pass "_" on.
    If 'output' if False - stop the calculation.
    '''
    # Get current input_

    input_ = locals_.get('_', None)

    if input_ is None:

        input_ = globals_.get('_', None)

    # Instance? (e.g. function, instance of class that implements __call__)

    if callable(output):

        output = __apply_output_to_input(output, input_, locals_, globals_)

        # Reset `ignore_iterables` if callable(), thus allowing a function return value to be iterated

        ignore_iterables = [str, unicode, dict]

    # Switch?

    else:

        if isinstance(output, dict):

            # NOTE: Private case, dict as a start of flow

            if input_ is not None:

                # 1 -> {1: 'One', 2: 'Two'} = 'One'

                output = output.get(input_, False)

                if output is False:

                    return (output, ignore_iterables, True)

    # Special Values

    if output is False:

        # 1 -> False = <Terminate resource>

        return (output, ignore_iterables, True)

    if output is True:

        # 1 -> True = 1

        output = input_

    if output is None:

        # 1 -> None = 1

        output = input_

    #return, all is good (so stop_calculation = False).

    return (output, ignore_iterables, False)


def __eval_single_object(output, operator, provider, expression, locals_, globals_, ignore_iterables):

    '''
    Treat object_or_objects as a single object, and evaluate it directly.
    The following outputs are "special":
    If 'output' is a function, apply it to '_' (the result of the last calculation).
    If 'output' is a dictionary - use it as a switch.
    If 'output' is True or None - pass "_" on.
    If 'output' if False - stop the calculation.
    Otherwise, pass it on to the next atom or list of atoms.
    '''

    return_value = []

    globals_values = []

    locals_values = []

    output, ignore_iterables, stop_calculation = __handle_special_outputs(output, locals_, globals_, ignore_iterables)

    if stop_calculation is True:

        return [False]

    # `output` is array or discrete?

    if not isinstance(output, tuple(ignore_iterables)) and __isiter(output):

        # Iterate `output`

        for item in output:

            globals_['_'] = locals_['_'] = item

            temp_locals_ = copy.copy(locals_)

            temp_globals_ = copy.copy(globals_)

            locals_values.append(temp_locals_)

            globals_values.append(temp_globals_)

            # Call next atom in expression with `item` as `input`

            if expression[1:]:

                # Synchronous

                if operator == '|':

                    current_return_value = provider.apply(__run, args=(expression[1:], temp_globals_, temp_locals_, True))

                # Asynchronous

                else:

                    current_return_value = provider.apply_async(__run, args=(expression[1:], temp_globals_, temp_locals_, True))

                return_value.append(current_return_value)

            else:

                return_value.append(item)

    else:

        temp_locals_ = copy.copy(locals_)

        temp_globals_ = copy.copy(globals_)

        locals_values.append(temp_locals_)

        globals_values.append(temp_globals_)

        # Same resource, next atom

        globals_['_'] = locals_['_'] = output

        if expression[1:]:

            globals_.update({'__ITERATE_LITERAL_ARRAYS__': True})

            # Call next atom in expression with `output` as `input`

            if isinstance(provider, multiprocessing.pool.ThreadPool):

                # Recycle worker

                return __run(expression[1:], globals_, locals_, provider)

            # Call provider.apply_async to evaluate next atom

            else:

                # NOTE: Provider changing effect is only lasting *1* call, thus, reverting to default after this call

                return_value.append(provider.apply_async(__run, args=(expression[1:], __pickle_safe_dict(temp_globals_), __pickle_safe_dict(temp_locals_), None)))

        else:

            return_value.append(output)

    # Join any async resources before returning

    provider.close()

    provider.join()

    return_value = __resolve_and_fix_results(return_value)

#    # Convert [[(1, {}, {})]] to [(1, {}, {})]
#
#    if return_value and len(return_value) == 1 and isinstance(return_value[0], list):
#
#        return_value = return_value[0]

    if len(globals_values) != 1:

        globals_, locals_ = __merge_all_globals_and_locals(temp_globals_, temp_locals_, globals_values[1:], {}, locals_values[1:], {})

    else:

        globals_, locals_ = temp_globals_, temp_locals_

    return return_value


def __change_provider_in_single(expression, operator, globals_, locals_):

    '''
    '''

    future_object = python.eval(expression[1][1], globals_, locals_)

    (new_globals_, new_locals_) = python.eval(future_object.get_attributes())

    # Update

    globals_.update(new_globals_)

    locals_.update(new_locals_)

    # Unpack __builtins.__attributedcode() (inc. explicit explicit to `operator`)

    expression[1] = python.eval(future_object.get_expression())

    return (expression, __create_pool(globals_, locals_))


def __run(expression, globals_, locals_, provider=None):

    # Setup

    resources = []

    globals_values = []

    locals_values = []

    (operator, atom) = expression[0]

    changed_provider = False

    ignore_iterables = [str, unicode, dict]

    return_value = None

    iterate_literal_arrays = globals_['__ITERATE_LITERAL_ARRAYS__']

    if not iterate_literal_arrays:

        ignore_iterables = ignore_iterables + [list, tuple]

    if not provider:

        provider = __create_default_pool(globals_, locals_)

    # Thread or Process?

    if expression[1:] and expression[1][1].startswith('__builtins__.attributedcode'):

        (expression, provider) = __change_provider_in_single(expression, operator, globals_, locals_)

        locals_ = __pickle_safe_dict(locals_)

        globals_ = __pickle_safe_dict(globals_)

    # Evaluate current atom, then either evaluate each element of the iterable separately,
    # or treat it as a single block.

    object_or_objects = __eval_current_atom(atom, locals_, globals_)

    if not isinstance(object_or_objects, tuple(ignore_iterables)) and __isiter(object_or_objects):

        return_value = __eval_multiple_objects(object_or_objects, operator, provider, expression, locals_, globals_)

    else:

        return_value = __eval_single_object(object_or_objects, operator, provider, expression, locals_, globals_, ignore_iterables)

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


def __merge_dicts(d1, d2, ignore_keys):

    result = dict(d1)

    for k, v in d2.iteritems():

        if k not in ignore_keys:

            if k in result:

                if result[k] != v:

                    # TODO: Is this the best way to handle multiple/different v`s of k?

                    del result[k]

                    ignore_keys.update({k: True})

            else:

                result[k] = v

    return result


def __merge_all_globals_and_locals(current_globals, current_locals, globals_list=[], ignore_globals_keys={}, locals_list=[], ignore_locals_keys={}):

    current_globals = __merge_dicts(current_globals, globals_list.pop(), ignore_globals_keys)

    current_locals = __merge_dicts(current_locals, locals_list.pop(), ignore_locals_keys)

    if not globals_list or not locals_list:

        return current_globals, current_locals

    return __merge_all_globals_and_locals(current_globals, current_locals, globals_list, ignore_globals_keys, locals_list, ignore_locals_keys)


def _is_referencing_underscore(expression):

    # e.g. [u'->', u'_']

    left_side = expression[0]

    # e.g. u'_'

    symbol = left_side[1]

    if symbol == '_':

        return True

    return False


def parse(source):
    """Parse the source into a tree (i.e. list of list).

    Args:
        source: A string representing a Pythonect code.

    Returns:
        A tree (i.e. list of list) of Pythonect symbols.

    Raises:
        SyntaxError: An error occurred parsing the code.
    """

    return parser.Parser().parse(source)


def eval(source, globals_={}, locals_={}):
    """Evaluate Pythonect code in the context of globals and locals.

    Args:
        source: A string representing a Pythonect code or a tree as
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

        return_values = []

        globals_values = []

        locals_values = []

        prog_return_blocks = None

        tasks = []

        if isinstance(source, list):

            expressions = source

        else:

            expressions = parse(source)

        # Extend Python's __builtin__ with Pythonect's `lang`

        start_globals_ = __extend_builtins(globals_)

        # Default input

        if start_globals_.get('_', None) is None:

            start_globals_['_'] = locals_.get('_', None)

        # Execute Pythonect program

        pool = __create_pool(globals_, locals_)

        # 2 ... N

        for current_expression in expressions[1:]:

            if globals_.get('__IN_EVAL__', None) is None and not _is_referencing_underscore(current_expression):

                # Reset '_'

                globals_['_'] = None

                locals_['_'] = None

            if globals_.get('__IN_EVAL__', None) is None:

                globals_['__IN_EVAL__'] = True

            temp_globals_ = copy.copy(globals_)

            temp_locals_ = copy.copy(locals_)

            task_result = pool.apply_async(__run, args=(current_expression, temp_globals_, temp_locals_, None))

            tasks.append((task_result, temp_locals_, temp_globals_))

        # 1 (i.e. N-1)

        if expressions:

            if globals_.get('__IN_EVAL__', None) is None and not _is_referencing_underscore(expressions[0]):

                # Reset '_'

                globals_['_'] = None

                locals_['_'] = None

            if globals_.get('__IN_EVAL__', None) is None:

                globals_['__IN_EVAL__'] = True

            result = __run(expressions[0], globals_, locals_, None)

            for expr_return_value in result:

                globals_values.append(globals_)

                locals_values.append(locals_)

                return_values.append(expr_return_value)

        # (2 ... N)

        for (task_result, task_locals_, task_globals_) in tasks:

            return_values.append(task_result.get())

            locals_values.append(task_locals_)

            globals_values.append(task_globals_)

        return_value = return_values

        # [...] ?

        if return_value:

            # Single return value? (e.g. [1])

            if len(return_value) == 1:

                return_value = return_value[0]

            # Update globals_ and locals_

            globals_, locals_ = __merge_all_globals_and_locals(globals_, locals_, globals_values, {}, locals_values, {})

        # Set `return value` as `_`

        globals_['_'] = locals_['_'] = return_value

        if globals_.get('__IN_EVAL__', None) is not None:

            del globals_['__IN_EVAL__']

    return return_value
