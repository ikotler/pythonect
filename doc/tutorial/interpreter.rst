.. _tut-using:

*******************************
Using the Pythonect Interpreter
*******************************

Pythonect provides an interpreter named ``pythonect`` for evaluating Pythonect programs and expressions interactively.


.. _tut-invoking:

Invoking the Interpreter
========================

Using the Pythonect interpreter is quite easy. Once the interpreter is :ref:`installed <installation>`, you're ready to go. You can invoke the interpreter from the command line as follows:
::

   $ pythonect

The interpreter prints its sign-on message and leaves you at its ``>>>`` prompt:
::

    Python 2.7.2 (default, Oct 11 2012, 20:14:37) 
    [Pythonect 0.5.0.dev12] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

In this interactive mode, you can evaluate arbitrary Pythonect expressions:
::

    >>> 1+1
    2
    >>> "Hello, world" -> print
    <MainProcess:MainThread> : Hello, world

To exit the interpreter, just type the ``quit`` command at the beginning of a line (on Unix systems, typing the end-of-file character :kbd:`Control-D` will do the same). 

Of course you can also run your scripts directly from the command line, as follows:
::
    $ pythonect myscript.p2y

This executes the script in batch mode. Add the :option:`-i` option if you prefer to run the script in interactive mode:
::

    $ pythonect -i myscript.p2y

A number of other command line options are available; try pythonect :option:`-h` for a list of those. 


.. _tut-interpenv:

The Interpreter and Its Environment
===================================


.. _tut-scripts:

Executable Pythonect Scripts
----------------------------

On BSD'ish Unix systems, Pythonect scripts can be made directly executable, like
shell scripts, by putting the line:
::

    #! /usr/bin/env pythonect

(assuming that the interpreter is on the user's :envvar:`PATH`) at the
beginning of the script and giving the file an executable mode.  The ``#!``
must be the first two characters of the file.

The script can be given an executable mode, or permission, using the
:program:`chmod` command::

    $ chmod +x myscript.p2y

It can also accept arguments from the command line (these are available in Pythonect by accessing ``sys.argv``), as follows:
::

    $ cat calc.p2y
    #! /usr/bin/env pythonect
    int(sys.argv[1]) + int(sys.argv[2]) -> print

    $ pythonect calc.p2y 1 2
    <MainProcess:MainThread> : 3


.. _tut-history:

The :file:`.pythonect_history` File
-----------------------------------

When running interactively, the Pythonect interpreter usually employs the GNU readline library to provide some useful command line editing facilities, as well as to save command history. The cursor up and down keys can then be used to walk through the command history, existing commands can be edited and resubmitted with the :kbd:`Enter` key, etc. The command history is saved in the :file:`.pythonect_history` file in your home directory between different invocations of the interpreter.