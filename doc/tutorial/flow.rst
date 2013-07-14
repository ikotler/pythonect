.. _tut-flow:

*********
Data Flow
*********

Depending on the scripting interface, directing the flow can be represented by plain text or interconnected lines


.. _tut-txtflow:

Text-based Symbols
==================

The text-based scripting language aims to combine the quick and intuitive feel of shell scripting. Adopting a *Unix Pipeline*-like syntax.


``|`` as Synchronous Forward
----------------------------

This operator pushs data to next operation and **do** block/wait for it
finish. For example:  
::

    [1,2,3,4] | print

Will always print (each item in it's own thread and in this order): ``1``, ``2``, ``3``, ``4``.


``->`` as Asynchronous Forward
------------------------------

This operator pushs data to the next operation and **do not** block/wait for
it to finish. For example:  
::

    [1,2,3,4] -> print

May print (each item in it's own thread): ``4``, ``3``, ``2``, ``1`` or ``2``, ``1``, ``3``, ``4`` or even ``1``, ``2``, ``3``, ``4``.


.. tut-graphflow:

"Boxes and Arrows"
==================

Currently, in the Visual Programming Language, all lines are treated as asynchronous forward.