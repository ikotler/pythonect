.. _installation:

Installation
============

This part of the documentation covers the installation of Pythonect. The first
step to using any software package is getting it properly installed. 

.. _installing:

--------------------
Installing Pythonect
--------------------

Pythonect works with Python version 2.6 and greater, but it will not work
(yet) with Python 3. Dependencies are listed in ``setup.py`` and will be
installed automatically as part of any of the techniques listed below.

Distribute & Pip
----------------

Installing Pythonect is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install pythonect

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install pythonect

.. note::

    Using easy_install is discouraged. Why? `Read here <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.


-------------------
Download the Source
-------------------

You can also install pythonect from source. The latest release (|version|) is available from GitHub.

* tarball_
* zipball_

Once you have a copy of the source, unzip or untar the package, change
directory into the extracted distribution and type::

    $ python setup.py install


To download the full source history from Git, see :ref:`Source Control <scm>`.

.. _tarball: http://github.com/ikotler/pythonect/tarball/master
.. _zipball: http://github.com/ikotler/pythonect/zipball/master


.. _updates:

Staying Updated
---------------

The latest version of Pythonect will always be available here:

* PyPi: http://pypi.python.org/pypi/pythonect/
* GitHub: http://github.com/ikotler/pythonect/

When a new version is available, upgrading is simple::

    $ pip install pythonect --upgrade
