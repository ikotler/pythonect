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

"""This file content extends the Python's __builtins__"""

import __builtin__


# Functions

def print_(object_):

    import threading

    import sys

    # START OF CRITICAL SECTION

    __builtin__.__GIL__.acquire()

    try:

        import multiprocessing

        if multiprocessing.current_process().name == 'MainProcess':

            sys.stdout.write("<%s:%s> : %s\n" % (multiprocessing.current_process().name, threading.current_thread().name, object_))

        else:

            sys.stdout.write("<PID #%d> : %s\n" % (multiprocessing.current_process().pid, object_))

    except ImportError:

            sys.stdout.write("<%s> : %s\n" % (threading.current_thread().name, object_))

    sys.stdout.flush()

    __builtin__.__GIL__.release()

    # END OF CRITICAL SECTION

    return None


# Classes

class expr(object):

    def __init__(self, expression):

        self.__expression = expression

    def __repr__(self):

        return self.__expression

    def __call__(self, globals_, locals_):

        import eval

        return eval.eval(self.__expression, globals_, locals_)


class remotefunction(object):

    def __init__(self, name, host, *args, **kwargs):

        self.__name = name.strip()

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
