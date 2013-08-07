psj.policy
**********

A package that defines the site policy of a PloneScholarlyJournal
site.

The ``Plone Scholarly Journal`` (PSJ) is a collection of packages to
create and maintain scientific scholarly journals using Plone.

The special abilities of PSJ are:

- High quality on-the-fly transformations of office documents using
  OpenOffice.org.

- Flexible metadata handling

This package contains the transforms to generate HTML and PDF docs
from input files in office format (``.doc``, ``.docx``, LibreOffice
docs).

Currently, the whole thing consists of three packages:

- ``psj.content`` (provides specialized content types with extended
  metadata handling)

- ``psj.policy`` (this package)


Prerequisites
=============

You need the following things to install this package:

- **Python 2.6 or 2.7**

  Currently Python 2.6 or 2.7 is needed to run Zope (Plone and
  psj). Python 2.7 is recommended.

  Also `python-dev` and the usual build tools are needed to build the
  devel environment.

- **git**

  `git` is needed to fetch development packages of `ulif.openoffice`
  that are not released already.

  Debian/Ubuntu users can install it via::

    $ sudo apt-get install git


Installation
============

First, make sure your system meets the requirements mentioned above.


Using `zc.buildout`
-------------------

We use `zc.buildout` to build a runnable, testable `psj` environment.

Bootstrap the initial buildout environment::

    $ python2.7 bootstrap.py -v 1.7.1

and run the buildout command::

    $ bin/buildout

Lots of stuff will be downloaded, compiled and installed here.

If you happen to change the values in `buildout.cfg`, you have to
'rebuild' the environment by running ``bin/buildout`` again.

You can run the tests using something like::

    $ bin/test


Using Python-eggs
-----------------

If you use `psj.policy` as part of another package, you can simply
install it using `pip` and the Python Package Index (PyPI).::

    $ pip install psj.policy

which will install the latest released version. If you have psj.policy
already installed, you can update using::

    $ pip install -U psj.policy
