.. _installation:

Installation
============

Pythonect works with Python version 2.6 and greater, but it will not work
(yet) with Python 3. Dependencies are listed in ``setup.py`` and will be
installed automatically as part of any of the techniques listed below.

.. _installation-pip:
 
Using pip or easy_install
-------------------------

Easiest way to install Pythonect is to use ``pip``:

.. code-block:: bash

   pip install Pythonect

And second to easiest is with ``easy_install``:

.. code-block:: bash

   easy_install Pythonect

.. note::

    Using easy_install is discouraged. Why? `Read here <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.

.. _installation-git:
 
Using git repository
--------------------

Regular development happens at our `GitHub repository
<https://github.com/ikotler/pythonect>`_. Grabbing the  cutting edge version
might give you some extra features or fix some newly discovered bugs. We
recommend not installing from the git repo unless you are actively developing
*Pythonect*. To clone the git repository and install it locally:

.. code-block:: bash

  git clone git://github.com/ikotler/pythonect.git
  cd pythonect
  python setup.py install

Alternatively, if you use pip, you can install directly from the git repository:

.. code-block:: bash

  pip install \
          git+git://github.com/ikotler/pythonect.git@master#egg=pythonect \
          -r https://github.com/ikotler/pythonect/raw/master/doc/requirements.txt

.. _installation-archives:
 
Using archives (tarball)
------------------------

Visit our `PyPI Page <https://pypi.python.org/pypi/Pythonect>`_ to grab the
archives of both current and previous stable releases. After untarring, simply
run ``python setup.py install`` to install it.