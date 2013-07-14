.. _tut-powerfeatures:

Power Features
==============

This section groups a few of Pythonect power features that one day may get their own section


Autoloader
-----------

Pythonect includes an autoloader functionally. You can access any functions,
attributes, etc. from a Python module without having to ``import`` it
first. For example:  
::

    "Hello, world" -> string.split | print

Will print (in that order, and in different threads): ``Hello,`` and
``world``. Another example: 
::

	sys.path -> print

Will print (in no particular order) every directory in your :const:`PATH`, as represented in your sys.path.


.. _tut-meta_amp:

Using ``&`` to Spawn a New Process
----------------------------------

Pythonect uses threads by default, but you can switch to processes by using the metacharacter ``&``. For example:
::

    "Hello, world" -> print &

This will print ``"Hello, world"`` from a new process. You can also mix and match:
::

    "Hello, world" -> [print, print &]

This will print ``"Hello, world"`` twice, one from a new thread and the other from a new process.

Notice that switch between thread and process is only valid for the duration of the function call/expression evaluation.


.. _tut-meta_at:

Using ``@`` to Remote Call
--------------------------

Pythonect lets you call functions remotely, by using the metacharacter ``@``. To demonstrate this, you will need to use the following simple server (written in Python):
::

    from SimpleXMLRPCServer import SimpleXMLRPCServer
    from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


    class RequestHandler(SimpleXMLRPCRequestHandler):
    	rpc_paths = ('/RPC2',)


    def say_hello(x):
    	return "Hello " + x + " and world"

    server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler)
    server.register_function(say_hello)
    server.serve_forever()

Save it as :file:`xmlrpc_srv.py` and run it. This code will run a Simple XML-RPC server that will export a function called ``say_hello``.

Now, calling ``say_hello`` from Pythonect is as easy as:
::

    "foobar" -> say_hello@xmlrpc://localhost:8000 -> print

This will print :const:`Hello foobar and world`. 

The destination hostname can also be the result of a function call, or an expression. For example:
::

    "foobar" -> say_hello@"xmlrpc://" + "localhost:8000" -> print

Or:
::

	"foobar" -> say_hello@"xmlrpc://" + get_free_host() -> print

Where ``get_free_host()`` is a fictional Python function that will return an available hostname from a list of hostnames.

As a loopback, you can use :const:`None` as an hostname to make the call locally. For example:
::
  
    "Hello, world" -> print@None

Is equal to:
::

    "Hello, world" -> print

Both will print ``"Hello, world"`` locally.