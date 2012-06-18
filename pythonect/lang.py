# This file content extends the Python's __builtins__

import __builtin__


# Functions

def print_(object):

    import multiprocessing

    import threading

    import sys

    # START OF CRITICAL SECTION

    __builtin__.__GIL__.acquire()

    sys.stdout.write("<%s:%s> : %s\n" % (multiprocessing.current_process().name, threading.current_thread().name, object))

    sys.stdout.flush()

    __builtin__.__GIL__.release()

    # END OF CRITICAL SECTION

    return None


# Classes

class remotefunction(object):

    def __init__(self, name, host, *args, **kwargs):

        self.__name = name

        self.__host = host

        self.__remote_fcn = None

        self.__remote_fcn_args = args

        self.__remote_fcn_kwargs = kwargs

    def __repr__(self):

        if self.__remote_fcn:

            return repr(self.__remote_fcn)

        else:

            return "%s(%s,%s)@%s" % (self.__name, self.__remote_fcn_args, self.__remote_fcn_kwargs, self.__host)

    def evaluate_host(self, globals_, locals_):

        try:

            self.__host = eval(self.__host, globals_, locals_)

        except SyntaxError, e:

            # CONST? As it is

            pass

    def __call__(self, *args, **kwargs):

        call_args = args

        call_kwargs = kwargs

        if self.__remote_fcn_args or self.__remote_fcn_kwargs:

            call_args = self.__remote_fcn_args

            call_kwargs = self.__remote_fcn_kwargs

        # Python XML-RPC

        if self.__host.startswith('xmlrpc://'):

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

        exec self.__statement in globals_, locals_

        # Restore `_`

        globals_['_'] = __original_input

        # Pass-through

        return globals_['_']
