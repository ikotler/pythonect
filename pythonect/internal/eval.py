import __builtin__ as python
import Queue as queue
import threading
import copy
import logging
import importlib
import types
import time


try:

    import multiprocessing

except ImportError:

    # TODO: Warn that Current Python implementation does not support Multiprocessing

    pass


# Local imports

import parser
import lang


# Global variables

global_interpreter_lock = threading.Lock()


def __isiter(object):

    try:

        iter(object)

        return True

    except TypeError as e:

        return False


def __pickable_dict(locals_or_globals):

    result = dict(locals_or_globals)

    for k, v in locals_or_globals.iteritems():

        if isinstance(v, types.ModuleType):

            del result[k]

    return result


def __queue_to_queue(source_queue, dest_queue):

    try:

        # While source queue contain return value(s)

        while True:

            (resource_return_value, resource_globals, resource_locals) = source_queue.get(True, 1)

            dest_queue.put((resource_return_value, resource_globals, resource_locals), True, 1)

    except queue.Empty:

        pass


def __run(expression, globals_, locals_, return_value_queue, iterate_literal_arrays, provider=threading.Thread):

    resources = []

    (operator, atom) = expression[0]

    changed_provider = False

    orig_return_value_queue = return_value_queue

    # Thread or Process?

    if expression[1:] and expression[1][1].startswith('__builtins__.attributedcode'):

        future_object = python.eval(expression[1][1], globals_, locals_)

        (ignored_value, new_provider, new_return_value_queue) = python.eval(future_object.get_attributes())

        if new_provider != provider:

            changed_provider = True

            return_value_queue = new_return_value_queue()

        provider = new_provider

        # Unpack __builtins.__attributedcode()

        expression[1] = python.eval(future_object.get_expression())

    ignore_iterables = [str, unicode, dict]

    if not iterate_literal_arrays:

        ignore_iterables = ignore_iterables + [list, tuple]

    # TODO: This is a hack to support instances, should be re-written. If atom is `literal` or `instance`, it should appear as a metadata/attribute

    try:

        object_or_objects = python.eval(atom, globals_, locals_)

    except NameError as e:

        try:

            import importlib

            # NameError: name 'os' is not defined

            mod_name = e.message.split()[1][1:-1]

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

    # [1,2,3] -> [a,b,c] =
    #       Thread 1: 1 -> [a,b,c]
    #       Thread 2: 2 -> [a,b,c]
    #       ...

    if not isinstance(object_or_objects, tuple(ignore_iterables)) and __isiter(object_or_objects):

        for item in object_or_objects:

            # TODO: This is a hack to prevent from item to be confused as fcn call and raise NameError.

            if isinstance(item, basestring):

                # i.e. [1, 'Hello'] -> eval() = [1, Hello] , this fixup Hello to be 'Hello' again

                item = "'" + item + "'"

            # Process? (i.e. 'Hello, world' -> [print, print &])

            if isinstance(item, lang.attributedcode):

                (ignored_value, new_provider, new_return_value_queue) = python.eval(item.get_attributes())

                if new_provider != provider:

                    changed_provider = True

                    return_value_queue = new_return_value_queue()

                provider = new_provider

                # Unpack __builtins.__attributedcode()

                expression = [(None, None), python.eval(item.get_expression())] + expression[1:]

                # Overwrite `item` with current input

                item = locals_.get('_', None)

                if isinstance(item, basestring):

                    # i.e. [1, 'Hello'] -> eval() = [1, Hello] , this fixup Hello to be 'Hello' again

                    item = "'" + item + "'"

            resource = provider(target=__run, args=([(operator, item)] + expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, not iterate_literal_arrays, provider))

            resource.start()

            # TODO: A patchy way to fix a timing bug that sometimes occur and causes the program to hang (reproduciton: 'Hello, world' -> [print, print &]' ; repeat until hangs)

            time.sleep(1)

            # Synchronous

            if operator == '|':

                resource.join()

                if changed_provider:

                    __queue_to_queue(return_value_queue, orig_return_value_queue)

            # Asynchronous

            else:

                resources.append(resource)

        # Asynchronous

        if resources:

            # Wait for resources

            for resource in resources:

                resource.join(None)

                if changed_provider:

                    __queue_to_queue(return_value_queue, orig_return_value_queue)

    # 1 -> [a,b,c]

    else:

        # Get current input

        input = locals_.get('_', None)

        if input is None:

            input = globals_.get('_', None)

        ####################################################
        # `output` = `input` applied on `object_or_objects`#
        ####################################################

        # Assume `object_or_objects` is literal (i.e. object_or_objects override input)

        output = object_or_objects

        # Instance? (e.g. function, instance of class that implements __call__)

        if callable(output):

            # Remote?

            if isinstance(output, lang.remotefunction):

                output.evaluate_host(globals_, locals_)

            # Python Statement?

            if isinstance(output, (lang.stmt, lang.expr)):

                output = output(globals_, locals_)

            else:

                output = output(input)

            # Reset `ignore_iterables` if callable(), thus allowing a function return value to be iterated

            ignore_iterables = [str, unicode, dict]

        # Switch?

        else:

            if isinstance(output, dict):

                # NOTE: Private case, dict as a start of flow

                if input is not None:

                    # 1 -> {1: 'One', 2: 'Two'} = 'One'

                    output = output.get(input, False)

                    if output is False:

                        return None

        # Special Values

        if output is False:

            # 1 -> False = <Terminate resource>

            return None

        if output is True:

            # 1 -> True = 1

            output = input

        if output is None:

            # 1 -> None = 1

            output = input

        # `output` is array or discrete?

        if not isinstance(output, tuple(ignore_iterables)) and __isiter(output):

            # Iterate `output`

            for item in output:

                globals_['_'] = locals_['_'] = item

                if expression[1:]:

                    # Call next atom in expression with `item` as `input`

                    resource = provider(target=__run, args=(expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, True, provider))

                    resource.start()

                    # Synchronous

                    if operator == '|':

                        resource.join()

                    else:

                        resources.append(resource)

                else:

                    return_value_queue.put((item, globals_, locals_))

        else:

            # Same resource, next atom

            globals_['_'] = locals_['_'] = output

            if expression[1:]:

                # If Thread, use the same thread, If Process, spawn a new one

                if provider == threading.Thread:

                    # Call next atom in expression with `output` as `input`

                    __run(expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, True)

                else:

                    # Process

                    resource = provider(target=__run, args=(expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, True))

                    resource.start()

                    resources.append(resource)

            else:

                return_value_queue.put((output, __pickable_dict(globals_), __pickable_dict(locals_)))

        # Asynchronous

        for resource in resources:

            resource.join(None)

            if changed_provider:

                __queue_to_queue(return_value_queue, orig_return_value_queue)


def __extend_builtins(globals_):

    # TODO: Is there any advantage to manually duplicate __builtins__, instead of passing our own?

    globals_['__builtins__'] = python

    # Add `pythonect.lang` to Python's `__builtins__`

    for name in dir(lang):

        # i.e. __builtins__.print_ = pythonect.lang.print_

        setattr(globals_['__builtins__'], name, getattr(lang, name))

    # Add GIL

    setattr(globals_['__builtins__'], '__GIL__', global_interpreter_lock)

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


def eval(source, globals_, locals_):
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

        waiting_list = []

        if isinstance(source, list):

            expressions = source

        else:

            expressions = parse(source)

        # Extend Python's __builtin__ with Pythonect's `lang`

        final_globals_ = __extend_builtins(globals_)

        # Default input

        if final_globals_.get('_', None) is None:

            final_globals_['_'] = locals_.get('_', None)

        # Iterate Pythonect program

        for expression in expressions:

            # Execute Pythonect expression

            resource_return_value_queue = queue.Queue()

            resource = threading.Thread(target=__run, args=(expression, final_globals_, locals_, resource_return_value_queue, True))

            resource.start()

            waiting_list.append((resource, resource_return_value_queue))

        # Join resources by execution order

        for (resource, resource_queue) in waiting_list:

            resource.join()

            try:

                # While queue contain return value(s)

                while True:

                    (resource_return_value, resource_globals, resource_locals) = resource_queue.get(True, 1)

                    resource_queue.task_done()

                    return_values.append(resource_return_value)

                    locals_values.append(resource_locals)

                    globals_values.append(resource_globals)

            except queue.Empty:

                pass

        return_value = return_values

        # [...] ?

        if return_value:

            # Single return value? (e.g. [1])

            if len(return_value) == 1:

                return_value = return_value[0]

            # Update globals_ and locals_

            new_globals, new_locals = __merge_all_globals_and_locals(globals_, locals_, globals_values, {}, locals_values, {})

            globals_.update(new_globals)

            locals_.update(new_locals)

        # [] ?

        else:

            return_value = False

        # Set `return value` as `_`

        globals_['_'] = locals_['_'] = return_value

    return return_value
