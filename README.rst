=========
Pythonect
=========

Pythonect_ is a new, experimental, general-purpose dataflow programming language based on Python. It provides both a visual programming language and a text-based scripting language. The text-based scripting language aims to combine the quick and intuitive feel of shell scripting, with the power of Python. The visual programming language is based on the idea of a diagram with “boxes and arrows”. Crazy? Most definitely. And yet, strangely enough, it works!

.. _Pythonect: http://www.pythonect.org

Hello, world
------------

Here is the canonical "Hello, world" example program in Pythonect::

	"Hello, world" -> print

Or:

.. image:: http://pythonect.org/HelloWorld2.png

See the `Pythonect documentation <http://docs.pythonect.org>`_ for a detailed walkthrough of the language and its features.

Installation
------------

There are a few ways to install Pythonect.

1. You can install directly from PyPI_ using ``easy_install`` or pip_::

        easy_install Pythonect

   or::

        pip install Pythonect

2. You can clone the git repository somewhere in your system::

        git clone git://github.com/ikotler/pythonect.git

   Then you should do following steps::

        cd pythonect
        python setup.py install

   Alternatively, if you use pip_, you can install directly from the git repository::

        pip install \
        	git+git://github.com/ikotler/pythonect.git@master#egg=pythonect \
		-r https://github.com/ikotler/pythonect/raw/master/doc/requirements.txt

For any of the above methods, if you want to do a system-wide installation, you will have to do this with *root* permissions (e.g. using ``su`` or ``sudo``).

.. _PyPI: http://pypi.python.org/pypi/Pythonect/
.. _pip: http://www.pip-installer.org/

Build Status |status|
---------------------

.. |status| image:: https://secure.travis-ci.org/ikotler/pythonect.png

Licensing
---------

Pythonect is available under the BSD 3-Clause License; see ``LICENSE`` for details.
