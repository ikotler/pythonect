import __builtin__ as python
import Queue as queue
import threading
import copy
import logging


# Local imports

import internal.parser
import lang


# Global variables

global_interpreter_lock = threading.Lock()


def __isiter(object):

    try:

        iter(object)

        return True

    except TypeError, e:

        return False


def __run(expression, globals_, locals_, return_value_queue, iterate_literal_arrays):

    threads = []

    (operator, atom) = expression[0]

    ignore_iterables = [str, unicode, dict]

    if not iterate_literal_arrays:

        ignore_iterables = ignore_iterables + [list, tuple]

    # TODO: This is a hack to support instances, should be re-written. If atom is `literal` or `instance`, it should appear as a metadata/attribute

    try:

        object_or_objects = python.eval(atom, globals_, locals_)

    except Exception, e:

        object_or_objects = atom

    # [1,2,3] -> [a,b,c] =
    #       Thread 1: 1 -> [a,b,c]
    #       Thread 2: 2 -> [a,b,c]
    #       ...

    if not isinstance(object_or_objects, tuple(ignore_iterables)) and __isiter(object_or_objects):

        for item in object_or_objects:

            thread = threading.Thread(target=__run, args=([(operator, item)] + expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, not iterate_literal_arrays))

            thread.start()

            # Synchronous

            if operator == '|':

                thread.join()

            # Asynchronous

            else:

                threads.append(thread)

        # Asynchronous

        if threads:

            # Wait for threads

            for thread in threads:

                thread.join(None)

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

            # Python Statement?

            if isinstance(output, (lang.stmt, lang.expr)):

                output = output(globals_, locals_)

            else:

                # TODO: This should be wraped in eval() otherwise `output()` can affect `__run` globals

                output = output(input)

            # Reset `ignore_iterables` if callable(), thus allowing a function return value to be iterated

            ignore_iterables = [str, unicode, dict]

        # Special Values

        if output is False:

            # 1 -> False = <Terminate Thread>

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

                    thread = threading.Thread(target=__run, args=(expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, True))

                    thread.start()

                    threads.append(thread)

                else:

                    return_value_queue.put(item)

        else:

            # Same thread, next atom

            globals_['_'] = locals_['_'] = output

            if expression[1:]:

                # Call next atom in expression with `output` as `input`

                __run(expression[1:], copy.copy(globals_), copy.copy(locals_), return_value_queue, True)

            else:

                return_value_queue.put(output)

        for thread in threads:

            thread.join(None)


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


def eval(source, globals_, locals_):

    return_value = []

    waiting_list = []

    # Parse Pythonect

    parser = internal.parser.Parser()

    # Extend Python's __builtin__ with Pythonect's `lang`

    final_globals_ = __extend_builtins(globals_)

    # Default input

    if final_globals_.get('_', None) is None:

        final_globals_['_'] = locals_.get('_', None)

    # Iterate Pythonect program

    for expression in parser.parse(source):

        # Execute Pythonect expression

        thread_return_value_queue = queue.Queue()

        thread = threading.Thread(target=__run, args=(expression, final_globals_, locals_, thread_return_value_queue, True))

        thread.start()

        waiting_list.append((thread, thread_return_value_queue))

    # Join threads by execution order

    for (thread, thread_queue) in waiting_list:

        thread.join()

        try:

            # While queue contain return value(s)

            while True:

                thread_return_value = thread_queue.get(True, 1)

                thread_queue.task_done()

                return_value.append(thread_return_value)

        except queue.Empty:

            pass

    # [...] ?

    if return_value:

        # Single return value? (e.g. [1])

        if len(return_value) == 1:

            return_value = return_value[0]

    # [] ?

    else:

        return_value = False

    # Set `return value` as `_`

    globals_['_'] = locals_['_'] = return_value

    return return_value
