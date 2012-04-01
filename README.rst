=========
Pythonect
=========

Pythonect is a new, experimental, general-purpose dataflow programming language based on Python, written in Python.
It aims to combine the intuitive feel of shell scripting (and all of its perks like implicit parallelism) with the flexibility and agility of Python.

Hello, world
------------

Here is the canonical "Hello, world" example program in Pythonect::
	
	"Hello, world" -> print
	
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

Licensing
---------

Pythonect is made available under a BSD license; see ``LICENSE`` for details.
