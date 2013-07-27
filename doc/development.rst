.. _development:

Development
===========

Pythonect is under active development, and contributors are welcome.

If you have a feature request, suggestion, or bug report, please open a new
issue on GitHub_. To submit patches, please send a pull request on GitHub_.

If you'd like to contribute, there's plenty to do. Here's a short todo list.

.. include:: ../TODO.rst


.. _GitHub: http://github.com/ikotler/pythonect/


.. _scm:

--------------
Source Control
--------------

Pythonect source is controlled with Git_, the lean, mean, distributed source
control machine.

The repository is publicly accessible.

    ``git clone git://github.com/ikotler/pythonect.git``

The project is hosted on **GitHub**:

    `http://github.com/ikotler/pythonect <http://github.com/ikotler/pythonect>`_

.. _Git: http://git-scm.org

Git Branch Structure
++++++++++++++++++++

Feature / Hotfix / Release branches follow a `Successful Git Branching Model <http://nvie.com/posts/a-successful-git-branching-model/>`_. `Git-Flow <http://github.com/nvie/gitflow>`_ is a great tool for managing the repository. I highly recommend it.

``develop``
    The "next release" branch. Likely unstable.
``master``
    Current production release (|version|) on PyPi.

Each release is tagged.

When submitting patches, please place your feature/change in its own branch prior to opening a pull request on GitHub_.


-----------------
Testing Pythonect
-----------------

Testing is crucial to Pythonect's stability. When developing a new feature for Pythonect, be sure to write proper tests for it as well.

The easiest way to test your changes for potential issues is to simply run the test suite directly: ::

    $ python setup.py nosetests

Don't have nose_ installed? Installing nose is simple: ::

    $ pip install nose

.. _nose: http://somethingaboutorange.com/mrl/projects/nose/


----------------------
Continuous Integration
----------------------

Every commit made to the **develop** branch is automatically tested and inspected upon receipt with `Travis CI <https://travis-ci.org/>`_. If you have access to the main repository and broke the build, you will receive an email accordingly.

Anyone may view the build status and history at any time:

    https://travis-ci.org/ikotler/pythonect

Additional reports will also be included here in the future, including :pep:`8` checks and stress reports for extremely large datasets.


.. _docs:

-----------------
Building the Docs
-----------------

Documentation is written in the powerful, flexible, and standard Python documentation format, `reStructured Text`_.
Documentation builds are powered by the powerful Pocoo project, Sphinx_. The :ref:`API Documentation <api>` is mostly documented inline throughout the module.

The Docs live in ``pythonect/doc``. In order to build them, you will first need to install Sphinx: ::

    $ pip install sphinx


Then, to build an HTML version of the docs, simply run the following from the **doc** directory: ::

    $ make html

Your ``doc/_build/html`` directory will then contain an HTML representation of the documentation, ready for publication on most web servers.

You can also generate the documentation in **epub**, **latex**, and **json**.


.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx.pocoo.org