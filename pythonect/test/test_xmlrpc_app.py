#!/usr/bin/python

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from select import select
import unittest
import socket
import threading
import os
import sys


# Local imports

import pythonect


## {{{ http://code.activestate.com/recipes/520583/ (r1)
class XMLRPCServer(SimpleXMLRPCServer):
    """
    A variant of SimpleXMLRPCServer that can be stopped.
    """
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)
        self.logRequests = 0
        self.closed = False

    def serve_until_stopped(self):
        self.socket.setblocking(0)
        while not self.closed:
            self.handle_request()

    def stop_serving(self):
        self.closed = True

    def get_request(self):
        inputObjects = []
        while not inputObjects and not self.closed:
            inputObjects, outputObjects, errorObjects = \
                select([self.socket], [], [], 0.2)
            try:
                return self.socket.accept()
            except socket.error:
                raise
## end of http://code.activestate.com/recipes/520583/ }}}


# Global Variables

thread = None
server = None


def setUpModule():

    global thread

    global server

    # Restrict to a particular path.

    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    # Create a stopable XMLRPC Server

    server = XMLRPCServer(("localhost", 8000), requestHandler=RequestHandler)

    server.register_introspection_functions()

    # Register a simple function
    def inc_function(x):
        return x + 1

    server.register_function(inc_function, 'inc')

    print "*** Starting XMLRPCServer on localhost:8000 with registered function \'inc\'"

    # Run the server's main loop (in a thread)

    thread = threading.Thread(target=server.serve_until_stopped)

    thread.start()

    server = server


def tearDownModule():

    print "*** Shutting down XMLRPCServer (localhost:8000)"

    server.stop_serving()

    thread.join(None)


class TestPythonectRemoting(unittest.TestCase):

    def test_int_async_remotefunction_const_host(self):

        self.assertEqual(pythonect.eval('1 -> inc@xmlrpc://localhost:8000', {}, {}), 2)

    def test_int_sync_remotefunction_const_host(self):

        self.assertEqual(pythonect.eval('1 | inc@xmlrpc://localhost:8000', {}, {}), 2)

    def test_int_async_remotefunction_with_args_const_host(self):

        self.assertEqual(pythonect.eval('1 -> inc(1)@xmlrpc://localhost:8000', {}, {}), 2)

    def test_int_sync_remotefunction_with_args_const_host(self):

        self.assertEqual(pythonect.eval('1 | inc(1)@xmlrpc://localhost:8000', {}, {}), 2)

    def test_int_async_remotefunction_literal_expr(self):

        self.assertEqual(pythonect.eval('1 -> inc@"xmlrpc://" + "localhost:8000"', {}, {}), 2)

    def test_int_sync_remotefunction_literal_expr(self):

        self.assertEqual(pythonect.eval('1 | inc@"xmlrpc://" + "localhost:8000"', {}, {}), 2)

    def test_int_async_remotefunction_with_args_literal_expr(self):

        self.assertEqual(pythonect.eval('1 -> inc(1)@"xmlrpc://" + "localhost:8000"', {}, {}), 2)

    def test_int_sync_remotefunction_with_args_literal_expr(self):

        self.assertEqual(pythonect.eval('1 | inc(1)@"xmlrpc://" + "localhost:8000"', {}, {}), 2)

    def test_int_async_remotefunction_expr(self):

        self.assertEqual(pythonect.eval('[host = "localhost"] -> 1 -> inc@"xmlrpc://" + host + ":8000"', {}, {}), 2)

    def test_int_sync_remotefunction_expr(self):

        self.assertEqual(pythonect.eval('[host = "localhost"] -> 1 | inc@"xmlrpc://" + host + ":8000"', {}, {}), 2)

    def test_int_async_remotefunction_with_args_expr(self):

        self.assertEqual(pythonect.eval('[host = "localhost"] -> 1 -> inc(1)@"xmlrpc://" + host + ":8000"', {}, {}), 2)

    def test_int_sync_remotefunction_with_args_expr(self):

        self.assertEqual(pythonect.eval('[host = "localhost"] -> 1 | inc(1)@"xmlrpc://" + host + ":8000"', {}, {}), 2)

# Standard XML-RPC does not support **kwargs

#       def test_int_async_remotefunction_with_kwargs(self):
#               self.assertEqual( pythonect.eval('1 -> inc(x=1)@xmlrpc://localhost:8000', {}, {}) , 2 )

#       def test_int_sync_remotefunction_with_kwargs(self):
#               self.assertEqual( pythonect.eval('1 | inc(x=1)@xmlrpc://localhost:8000', {}, {}) , 2 )
