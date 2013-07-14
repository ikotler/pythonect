:orphan:

Welcome to Pythonect
====================

Welcome to Pythonect's documentation. This documentation is divided into
different parts. I recommend that you get started with :ref:`installation` and
then head over to the :ref:`tutorial`. If you'd rather dive into the internals
of Pythonect, check out the :ref:`api` documentation.

Pythonect is dependent on one external library: the `NetworkX
<http://networkx.github.io/>`_ graph library. This library is not documented
here. If you want to dive into its documentation, check out the following
link: `NetworkX Documentation <http://networkx.github.io/documentation/latest/>`_

.. note::
   This is the main documentation for the Pythonect project. The contents of
   this site are automatically generated via `Sphinx <http://sphinx-
   doc.org/>`_ based on the Python docstrings throughout the code and the
   reStructuredText documents in the `doc/ directory
   <https://github.com/ikotler/pythonect/tree/master/doc>`_ of the git
   repository. If you find an error in the documentation, please report it in
   the bug tracker `here <https://www.github.com/ikotler/pythonect/issues>`__,
   or even better, submit a pull request!

User's Guide
------------

This part of the documentation, which is mostly prose, begins with some
background information about Pythonect, then focuses on step-by-step
instructions for building applications with Pythonect.

.. toctree::
   :maxdepth: 2

   foreword
   installation
   tutorial/index

.. _api:

API Reference
-------------

If you are looking for information on a specific function, class or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api

Additional Notes
----------------

Design notes, legal information and changelog are here for the interested.

.. toctree::
   :maxdepth: 2

   changelog
   license