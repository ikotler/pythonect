Pythonect
=========

.. image:: https://badge.fury.io/py/Pythonect.png
    :target: http://badge.fury.io/py/Pythonect
    :alt: Latest version

.. image:: https://travis-ci.org/ikotler/pythonect.png?branch=master
    :target: https://travis-ci.org/ikotler/pythonect
    :alt: Travis-CI

.. image:: https://pypip.in/d/Pythonect/badge.png
    :target: https://crate.io/packages/Pythonect/
    :alt: Number of PyPI downloads

Homepage: `http://www.pythonect.org/ <http://www.pythonect.org/>`_

`Pythonect` is a new, experimental, general-purpose dataflow programming
language based on Python. It provides both a visual programming language and a
text-based scripting language. The text-based scripting language aims to
combine the quick and intuitive feel of shell scripting, with the power of
Python. The visual programming language is based on the idea of a diagram with
“boxes and arrows”. Crazy? Most definitely. And yet, strangely enough, it
works!


Hello, world
------------

Here is the canonical "Hello, world" example program in Pythonect::

	"Hello, world" -> print

Or:

.. image:: http://pythonect.org/HelloWorld2.png


Installation
------------

There are a few ways to install Pythonect.

1. You can install directly from PyPI_ using `setuptools/easy_install <http://pypi.python.org/pypi/setuptools>`_ or pip_::

        pip install Pythonect

   or::

        easy_install Pythonect

2. You can clone the git repository somewhere in your system::

        git clone git://github.com/ikotler/pythonect.git

   Then you should do following steps::

        cd pythonect
        python setup.py install

   Alternatively, if you use pip_, you can install directly from the git repository::

        pip install \
        	git+git://github.com/ikotler/pythonect.git@master#egg=pythonect \
		-r https://github.com/ikotler/pythonect/raw/master/doc/requirements.txt

For any of the above methods, if you want to do a system-wide installation,
you will have to do this with *root* permissions (e.g. using ``su`` or
``sudo``).

.. _PyPI: http://pypi.python.org/pypi/Pythonect/
.. _pip: http://www.pip-installer.org/


Examples
--------

See more examples at the `Pythonect Tutorial <http://docs.pythonect.org/en/latest/tutorial/index.html>`_.


Documentation
-------------

Full documentation is available at http://docs.pythonect.org/.


Please Help Out
---------------

This project is still under development. Feedback and suggestions are very
welcome and I encourage you to use the `Issues list
<http://github.com/ikotler/pythonect/issues>`_ on GitHub to provide that
feedback.

Feel free to fork this repo and to commit your additions. For a list of all
contributors, please see the `AUTHORS
<https://github.com/ikotler/pythonect/blob/master/AUTHORS>`_ file.

Any questions, tips, or general discussion can be posted to our Google group:
`http://groups.google.com/group/pythonect <http://groups.google.com/group
/pythonect>`_


Licensing
---------

Pythonect is published under the liberal terms of the BSD 3-Clause License,
see the `LICENSE <https://github.com/ikotler/pythonect/blob/master/LICENSE>`_
file. Although the BSD License does not require you to share any modifications
you make to the source code, you are very much encouraged and invited to
contribute back your modifications to the community, preferably in a GitHub
fork, of course.


Showing Your Appreciation
=========================

The best way to show your appreciation for Pythonect remains contributing to
the community. If you'd like to show your appreciation in another way,
consider Flattr'ing or Gittip'ing me:

|FlattrThis|_ |GittipThis|_

.. |GittipThis| image:: https://www.gittip.com/assets/10.0.6/logo.png
.. _GittipThis: https://www.gittip.com/ikotler

.. |FlattrThis| image:: http://api.flattr.com/button/button-static-50x60.png
.. _FlattrThis: https://flattr.com/thing/1713050/ikotlerpythonect-on-GitHub
