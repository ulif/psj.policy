psj.policy
**********

A package that defines the site policy of a PloneScientificJournal
site.

Use the psj.site package to see some actions.

The only thing that is built when installing the source version of
this package is a testrunner. This is good for development, but
endusers might get the psj.site package.

Prerequisites
=============

You need the following things to install this package:

- **Python 2.4**

  Currently Python 2.4 is needed to run Zope (Plone and psj). You can
  find out, whether you have Python 2.4 installed by opening a shell
  and entering::

    $ python -V

  This should give you something like::

    Python 2.4.3

  Note, that the whole thing won't work with Python <= 2.3 nor with
  newer versions (>= 2.5).


- **`easy_install` and Python `setuptools`**

  If you don't have `easy_install` already available, you can find the
  script to set it up on the `PEAK EasyInstall page` at:

    http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install

  You need to download `ez_setup.py`, which is available at:

    http://peak.telecommunity.com/dist/ez_setup.py

  Then, you run it like this to install ``easy_install`` into your
  system Python::

    $ sudo python2.4 ez_setup.py

  This will make ``easy_install-2.4`` available to you.

  Then you can install the Python ``setuptools`` simply by entering::

    $ sudo easy_install-2.4 setuptools

- **The Python UNO libs**

  The Python version you use here, must provide the ``pyuno``
  library. This library is needed to talk to the locally started
  OpenOffice.org (OOo) server. You can check this by typing::

     $ python2.4 -c 'import uno'

  If you get an error message, then  you're into trouble. Some Linux
  distributions offer a pyuno package for the system Python. Ubuntu
  users can install it like this::

     $ apt-get install python-uno

  Workaround:

    For Linux systems that have no pyuno installed, also the following
    approach is known to work:

    Modify the ``openoffice`` section in ``buildout.cnf`` such, that
    it reads::

      ...
      install-pyuno-egg = yes
      ...

    Then run buildout again. Afterwards, you have to set the
    ``LD_LIBRARY_PATH`` to::

      <YOURBUILDOUTPATH>/parts/openoffice/program

    before starting any of the generated scripts. For example instead
    of simply::

      $ bin/instance

    you must use::

      $ LD_LIBRARY_PATH=<YOURBUILDOUTPATH>/parts/openoffice/program \
         bin/instance

    or put this path into your system wide library path (something you
    don't want to do).


Installation
============

First, make sure your system meets the requirements mentioned above.

`psj` uses a `zc.buildout`-driven installation process, that has to be
initialized first. Because ``buildout`` needs a fairly recent version
of ``setuptools``, you should update your version of it::

    $ sudo easy_install -U setuptools

This brings ``setuptools`` to the newest version available.

Now, we are ready to go. Bootstrap the initial buildout environment::

    $ python2.4 bootstrap/bootstrap.py

and run the buildout command::

    $ bin/buildout

Lots of stuff will be downloaded, compiled and installed here.

Note that if you have more than one sandbox for a Zope-based web
application, it will probably make sense to share the eggs between the
different sandboxes.  You can tell zc.buildout to use a central eggs
directory by creating ``~/.buildout/default.cfg`` with the following
contents::

    [buildout]
    eggs-directory = /home/bruno/buildout-eggs

If you happen to change the values in `buildout.cfg`, you have to
'rebuild' the environment by running ``bin/buildout`` again.

You can run the tests using something like::

    $ bin/instance test -s psj.policy
