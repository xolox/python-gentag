gentag: Simple and powerful tagging for Python objects
======================================================

.. image:: https://travis-ci.org/xolox/python-gentag.svg?branch=master
   :target: https://travis-ci.org/xolox/python-gentag

.. image:: https://coveralls.io/repos/xolox/python-gentag/badge.svg?branch=master
   :target: https://coveralls.io/r/xolox/python-gentag?branch=master

The Python package `gentag` provides simple and powerful tagging for arbitrary
Python objects. After defining your tags and associated objects you can query
for the difference, intersection and union of tags to select specific objects.
The package is currently tested on cPython 2.6, 2.7, 3.4, 3.5, 3.6 and PyPy
(2.7).

.. contents::
   :local:

Status
------

While the ideas behind `gentag` have been floating around in my head since
2012 I didn't publish this as a standalone Python package until 2018 which
explains why I'm publishing the initial version as a beta. Looking ahead
towards the future:

- It may be that the current version serves my needs fine and at some point I
  decide to replace the 'beta' label with a 'stable' label without making any
  substantive changes.

- Releasing `gentag` is one step in the direction of releasing another Python
  package that I've been thinking about for a very long time now and if I turn
  out to have trouble integrating `gentag` into that package I won't hesitate
  to make (potentially major) changes to `gentag`.

Installation
------------

The `gentag` package is available on PyPI_ which means installation should be
as simple as:

.. code-block:: sh

   $ pip install gentag

There's actually a multitude of ways to install Python packages (e.g. the `per
user site-packages directory`_, `virtual environments`_ or just installing
system wide) and I have no intention of getting into that discussion here, so
if this intimidates you then read up on your options before returning to these
instructions ;-).

.. _usage:

Usage
-----

The following sections give an overview of how to get started. For more details
about the Python API please refer to the API documentation available on `Read
the Docs`_.

.. contents::
   :local:

Creating a scope
~~~~~~~~~~~~~~~~

To get started you have to create a Scope_ object:

.. code-block:: python

   >>> from gentag import Scope
   >>> tags = Scope()

The purpose of Scope_ objects is to group together related tags into an
evaluation context for tag expressions.

Defining tags
~~~~~~~~~~~~~

Scope_ instances allow you to define tags and associated objects:

.. code-block:: python

   >>> tags.define('archiving', ['deb', 'tar', 'zip'])
   >>> tags.define('compression', ['bzip2', 'deb', 'gzip', 'lzma', 'zip'])
   >>> tags.define('encryption', ['gpg', 'luks', 'zip'])

.. _querying tags:

Querying tags
~~~~~~~~~~~~~

Once you've defined some tags and associated objects you can query them,
for example here we query for the union of two tags:

.. code-block:: python

   >>> tags.evaluate('archiving | encryption')
   ['deb', 'gpg', 'luks', 'tar', 'zip']

These tag expressions can get arbitrarily complex:

.. code-block:: python

   >>> tags.evaluate('(archiving | encryption) & compression')
   ['deb', 'zip']

Supported operators
+++++++++++++++++++

The following operators can be used to compose tags:

========  ====================
Operator  Set operation
========  ====================
``&``     intersection
``|``     union
``-``     difference
``^``     symmetric difference
========  ====================

These operators create new Tag_ objects that can be composed further. Although
tags composed at runtime in Python syntax don't have a name, it is possible
define named composite tags using the `Scope.define()`_ method (see below).

The default tag
+++++++++++++++

There's one special tag that is always available under the name 'all'. As you
might have guessed it provides access to a set with all tagged objects:

.. code-block:: python

   >>> tags.evaluate('all')
   ['bzip2', 'deb', 'gpg', 'gzip', 'luks', 'lzma', 'tar', 'zip']

This can be useful to select all but a specific tag of objects:

.. code-block:: python

   >>> tags.evaluate('all - encryption')
   ['bzip2', 'deb', 'gzip', 'lzma', 'tar']

Named composite tags
~~~~~~~~~~~~~~~~~~~~

The expressions shown in the `querying tags`_ section above demonstrate that
tags can be composed using set operators. You can also define a named tag based
on an expression:

.. code-block:: python

   >>> tags.define('flexible', 'archiving & compression & encryption')

Such named composite tags can be evaluated like regular tags:

.. code-block:: python

   >>> tags.evaluate('flexible')
   ['zip']

You can also nest composite tags inside other composite tags.

History
-------

The example in the usage_ section isn't actually very useful, this is partly
because I didn't want a complicated subject matter to distract readers from
usage instructions :-).

The actual use case that triggered the ideas behind `gentag` presented itself
to me in 2012 when I wanted to query a database of more than 200 Linux server
names categorized by aspects such as:

- The distributor id (a string like 'debian' or 'ubuntu').
- The distribution codename (a string like 'trusty' or 'xenial').
- The server's role (database, mailserver, webserver, etc).
- The server's environment (production, development).

The easy selection of subsets of servers for my Python programs to operate on
quickly evolved into my main interface for selecting groups of servers. Since
then I've wanted to use similar functionality in other places, but found it too
much work to develop one-off solutions. This is how `gentag` was born.

About the name
~~~~~~~~~~~~~~

The name `gentag` stands for "generative tags", because the package allows new
tags to be composed (generated) from existing tags. I'd like to thank my
colleague `Seán Murphy <https://github.com/seanonmurphy>`_ for coming up with
this name :-).

Contact
-------

The latest version of `gentag` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2018 Peter Odding.

.. External references:
.. _GitHub: https://github.com/xolox/python-gentag
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _per user site-packages directory: https://www.python.org/dev/peps/pep-0370/
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/gentag
.. _Python: https://www.python.org/
.. _Read the Docs: https://gentag.readthedocs.org/en/latest/
.. _Scope.define(): https://gentag.readthedocs.org/en/latest/#gentag.Scope.define
.. _Scope: https://gentag.readthedocs.org/en/latest/#gentag.Scope
.. _Tag: https://gentag.readthedocs.org/en/latest/#gentag.Tag
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/
