# This file content extends the Python's __builtins__

import __builtin__


# Functions

def print_(object):

    import threading

    import sys

    # START OF CRITICAL SECTION

    __builtin__.__GIL__.acquire()

    try:

        import multiprocessing

        if multiprocessing.current_process().name == 'MainProcess':

            sys.stdout.write("<%s:%s> : %s\n" % (multiprocessing.current_process().name, threading.current_thread().name, object))

        else:

            sys.stdout.write("<PID #%d> : %s\n" % (multiprocessing.current_process().pid, object))

    except ImportError:

            sys.stdout.write("<%s> : %s\n" % (threading.current_thread().name, object))

    sys.stdout.flush()

    __builtin__.__GIL__.release()

    # END OF CRITICAL SECTION

    return None


# Classes

class attributedcode(object):

    def __init__(self, expression, attributes):

        self.__attributes = attributes

        self.__expression = expression

    def get_expression(self):

        return self.__expression

    def get_attributes(self):

        return self.__attributes


class remotefunction(object):

    def __init__(self, name, host, *args, **kwargs):

        self.__name = name

        self.__host = host

        self.__remote_fcn = None

        self.__remote_fcn_args = args

        self.__remote_fcn_kwargs = kwargs

        self.__locals = None

        self.__globals = None

    def __repr__(self):

        if self.__remote_fcn:

            return repr(self.__remote_fcn)

        else:

            return "%s(%s,%s)@%s" % (self.__name, self.__remote_fcn_args, self.__remote_fcn_kwargs, self.__host)

    def evaluate_host(self, globals_, locals_):

        self.__locals = locals_

        self.__globals = globals_

        try:

            self.__host = eval(self.__host, globals_, locals_)

        except SyntaxError as e:

            # CONST? As it is

            pass

    def __call__(self, *args, **kwargs):

        call_args = args

        call_kwargs = kwargs

        if self.__remote_fcn_args or self.__remote_fcn_kwargs:

            call_args = self.__remote_fcn_args

            call_kwargs = self.__remote_fcn_kwargs

        # Pseudo Protocol

        if self.__host is None or self.__host.startswith('None'):

            self.__remote_fcn = eval(self.__name, self.__globals, self.__locals)

        # Python XML-RPC

        elif self.__host.startswith('xmlrpc://'):

            import xmlrpclib

            # xmlrpc:// = http://, xmlrpcs:// = https://

            remote_srv = xmlrpclib.ServerProxy(self.__host.replace('xmlrpc', 'http', 1))

            self.__remote_fcn = getattr(remote_srv, self.__name)

        return self.__remote_fcn(*call_args, **call_kwargs)


class expr(object):

    def __init__(self, expression):

        self.__expression = expression

    def __repr__(self):

        return self.__expression

    def __call__(self, globals_, locals_):

        import eval

        return eval.eval(self.__expression, globals_, locals_)


class stmt(object):

    def __init__(self, statement):

        self.__statement = statement

    def __repr__(self):

        return self.__statement

    def __call__(self, globals_, locals_):

        # eval.eval() change's `_` value for `PythonectInteractiveConsole`.
        # Thus, any statement that includes `expr` might change current `_`

        # Save `_`

        __original_input = globals_.get('_', None)

        try:

            exec self.__statement in globals_, locals_

        except NameError as e:

                try:

                    import importlib

                    # NameError: name 'os' is not defined

                    mod_name = e.message.split()[1][1:-1]

                    globals_.update({mod_name: importlib.import_module(mod_name)})

                    exec self.__statement in globals_, locals_

                except Exception as e1:

                    # raise original Exception

                    raise e

        # Restore `_`

        globals_['_'] = __original_input

        # Pass-through

        return globals_['_']
