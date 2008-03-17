psj.policy.transforms
*********************

:Author: Uli Fouquet
:Test-Layer: unit

One of the major aims of Plone Scientific Journal sites is, to process
content, that was delivered in .odt or .docx formats. Transforms are
the Plone way to handle such 'external' document formats.

Currently supported is a set of transformations for XML based document
formats like OpenOffice.orgs `.odt` and Microsofts `.docx`
format. Those formats share the attribute to be in fact zipped XML
files.

The current transformations provided are:

- odt to HTML via lxml.

- odt to HTML via OpenOffice.org (OOo)

- docx to HTML via lxml.

The ``lxml`` library is a Python library that offers direct access to
systems' libxml2 and libxslt. The external `xsltproc` program, often
needed by other packages is not needed with `psj.policy` any more.

XSLT transformations
====================

XSLT stylesheets provide a set of rules to apply on an XML
file. Normally they provide substitutions that for example turn plain
XML into XHTML or similar.

The transoformations in the ``psj.policy`` package are performed by a
litte function in the ``xslttrans`` module::

   >>> from psj.policy.transforms.xslttrans import xslt_transform

This function expects two filedescriptors: the first for the XSLT
stylesheet, the second for the document, to which the stylesheet
should be applied. We create both::

   >>> xslt = '''<?xml version="1.0"?>
   ... <xsl:stylesheet version="1.0"
   ...     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
   ...   <xsl:output method = "xml"
   ...       encoding = "utf-8"
   ...       media-type = "application/xhtml+xml"
   ...       indent = "no"
   ...       doctype-public = "-//W3C//DTD XHTML 1.0 Transitional//EN"
   ...   />
   ...   <xsl:template match="/document">
   ...   <html><head><title>Test</title></head><body>
   ...     <h1>Hello!</h1>
   ...     <xsl:apply-templates />
   ...   </body></html>
   ...   </xsl:template>
   ... </xsl:stylesheet>
   ... '''

   >>> xml = '''<?xml version="1.0"?>
   ... <document>Blah</document>
   ... '''

We fake the filedescriptors using ``StringIO`` streams and call the
transformation engine::

   >>> from StringIO import StringIO
   >>> res = xslt_transform(StringIO(xslt), StringIO(xml))
   >>> res
   <lxml.etree._XSLTResultTree object at 0x...>

The generated document is available as string representation of the
result::

   >>> print str(res)
   <?xml version="1.0" encoding="utf-8"?>
   ...<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "">
   ...<html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>Test</title></head><body><h1>Hello!</h1>Blah</body></html>

Convert .odt to HTML
====================

For example we can use a transformation from .odt files to HTML. The
transformation is handled by the ``Odt2Html`` class::

   >>> from psj.policy.transforms.odt_to_html import Odt2Html

But this class in fact is merely a wrapper around the real document
converter defined in the ``xslttrans.Document`` class. This converter
is used by default for odt-to-HTML transformations.

We provide, however, also a converter, that uses an external programme
called ``xsltproc``, which normally comes with libxml/libxslt. This
converter is defined in ``cmd_xsltproc.Document``.

All converters that run external commands in here are named
``cmd_<progname>``, while all transformers are named after the
transformation they perform, for instance ``odt_to_html``.

While transformations call the converters to do the hard work, they
store the results into cache of the Plone instance.

All the testfiles we want to compare reside in the ``tests``
subdirectory::

   >>> from os.path import join, dirname
   >>> input_path = join(dirname(__file__), 'tests', 'input')
   >>> output_path = join(dirname(__file__), 'tests', 'output')

First we want to compare two files called ``testdoc1``::

   >>> input_file_path = join(input_path, 'testdoc1.odt')
   >>> expected_html = join(output_path, 'testdoc1.html')
   >>> expected_text = join(output_path, 'testdoc1.txt')


Create a virtual odt document (with xsltproc)
---------------------------------------------

To perform a conversion, we must create a document object first. This
is done by passing a document name (normally a filename) and the file
content to the constructor. We get the file contents::

   >>> content_in = r'' + open(input_file_path, 'rb').read()

Now, let's have a look at the converter::

   >>> from psj.policy.transforms.cmd_xsltproc import Document
   >>> document = Document('myodtdoc.odt', content_in)
   >>> document
   <psj.policy.transforms.cmd_xsltproc.Document instance at 0x...>

Note, that we gave a different 'filename' (``myodtdoc.odt``, than the
original filename (``testdoc1.odt``). That does not matter, because
from this point, the source file itself will not be touched any more.

We do not have to pass filenames with filename extension `odt`, but if
we do not, it will be appended::

   >>> document = Document('myodtdoc.doc', content_in)
   >>> document.fullname
   '...myodtdoc.doc.odt'

Complex documents like office docs often are built from several nested
docs. For example there could be images or other media contained in
the source. Therefore, while extracting the source file, a temporary
directory is created in filesystem, that can hold several documents on
different levels. We cannot know the directory's name completely in
advance, but it will start with ``tmp``::

   >>> import os.path
   >>> os.path.basename(document.tmpdir)
   'tmp...'

When a document is not needed anymore, the temporary directory will be
removed (this, unfortunately, is not a default behaviour and a
security risk if not done properly)::

   >>> tmp_path = document.tmpdir
   >>> os.path.isdir(tmp_path)
   True

   >>> del document
   >>> os.path.isdir(tmp_path)
   False

The destructor also checks, whether the temporary directory still
exists::

   >>> document = Document('myodtdoc.doc', content_in)
   >>> from shutil import rmtree
   >>> rmtree(document.tmpdir)
   >>> document.__del__() is None
   True

Otherwise we would get an error here.


Create a virtual odt document (with xslttrans)
----------------------------------------------

There is another module that we can use for XSLT transforms. While
``xsltproc`` used in the above section is an external binary, that
must be available at runtime, we can archive the same effect by using
the Python ``lxml`` module (version >= 2). One of the major advances
of this transformation is, that is does not need external binaries and
does also work on non-POSIX-compliant machines.

A transfrom using this module is defined in ``xslttrans.py``. It also
provides a ``Document`` class::

   >>> from psj.policy.transforms.xslttrans import Document

When we create a virtual XSLT document here, we must give an XSLT
stylesheet, which defines the real transformation from XML to, for
example, HTML::

   >>> stylesheet = os.path.join(
   ...     os.path.dirname(__file__), 'document2xhtml.xsl')

Now we can create the virtual document like this::

   >>> document = Document('myfile.odt', content_in,
   ...                     xsl_stylesheet_path=stylesheet)
   >>> document
    <psj.policy.transforms.xslttrans.Document instance at 0x...>

This type of document provides a ``fullname`` and a ``tmpdir``. What

   >>> document.fullname.endswith('myfile.odt')
   True

   >>> isinstance(document.tmpdir, basestring)
   True

When a document is not needed anymore, the temporary directory will be
removed (this, unfortunately, is not a default behaviour and a
security risk if not done properly)::

   >>> tmp_path = document.tmpdir
   >>> os.path.isdir(tmp_path)
   True

   >>> del document
   >>> os.path.isdir(tmp_path)
   False

The destructor also checks, whether the temporary directory still
exists::

   >>> document = Document('myodtdoc.doc', content_in)
   >>> from shutil import rmtree
   >>> rmtree(document.tmpdir)
   >>> document.__del__() is None
   True

Otherwise we would get an error here.


Convert the virtual document to HTML
------------------------------------

We can now call the converter, to retrieve a transformed
document. Which transformation is done, depends on the XSL stylesheet
given. In our case it should be HTML::

   >>> document = Document('myodtdoc', content_in,
   ...                     xsl_stylesheet_path=stylesheet)
   >>> output = document.convert()

The ``output`` variable now contains our XHTML result::

   >>> print output
   <?xml version="1.0" encoding="utf-8"?>
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ...>
   <html xmlns="http://www.w3.org/1999/xhtml">...</html>

This data should be equal to the data in ``testdoc1-xslttrans.html``::

   >>> expected_html = join(output_path, 'testdoc1-xslttrans.html')
   >>> expected_data = open(expected_html, 'r').read()
   >>> expected_data == output
   True

We also get a diff of both files::

   >>> import difflib
   >>> diff = difflib.unified_diff(expected_data.split('\n'),
   ...                             output.split('\n'))
   >>> list(diff)
   []

All this is very well, but now we also want OOo documents
automatically to be recognized and handled approprietely.


Transform data from .odt files
==============================

Transformations, different to simple conversions, take care of MIME
types and handle data in so-called `datastreams`. 

We now want to *transform* the ``testdoc1.odt`` document. For this, we
must create a transformation object first, which afterwards can
perform a transformation.


Create a transformation
-----------------------

Furthermore, we pick up our transformation. It is defined in the
``odt_to_html`` module, but we get an instance of the real
transformation class by calling ``register()``

   >>> from psj.policy.transforms import odt_to_html
   >>> transform = odt_to_html.register()
   >>> transform
   <psj.policy.transforms.odt_to_html.Odt2Html object at 0x...>

A transform should alway implement ``itransform``::

   >>> from Products.PortalTransforms.interfaces import itransform
   >>> itransform.isImplementedBy(transform)
   1

   >>> from Interface.Verify import verifyObject
   >>> verifyObject(itransform, transform)
   1

XXX: The interface implementations (and checks of them) here are old
Zope 2, because ``itransform`` is. This should be fixed in
``PortalTransforms``.

Transformations provide a name::

   >>> transform.name()
   'odt_to_html'

Furthermore they provide a list of input MIME types, a single output
MIME type and (some) an output encoding::

   >>> transform.inputs
   ('application/vnd.oasis.opendocument.text',)

   >>> transform.output
   'text/html'

   >>> transform.output_encoding
   'utf-8'


Perform a transformation
------------------------

For this, we again get the raw data from the document::

   >>> raw_odt = open(input_file_path).read()


Then, we need a new 'datastream', in wich the results will be
stored::

   >>> from Products.PortalTransforms.data import datastream
   >>> data = datastream('odt_to_html')

Now we can perform the real conversion in a transformation context::

   >>> res_data = transform.convert(raw_odt, data, 
   ...                              filename='testdoc1.odt')

Thre result stream should implement ``idatastream``::

   >>> from Products.PortalTransforms.interfaces import idatastream
   >>> idatastream.isImplementedBy(res_data)
   1

This stream can be read. We get the data::

   >>> got = res_data.getData()
   >>> print got
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
   <HTML>
   ...
   </HTML>

The result should look like the expected output we put in
``tests/output/testdoc1.html``::

   >>> expected_html = join(output_path, 'testdoc1.html')
   >>> expected_data = open(expected_html, 'r').read()
   >>> diff = difflib.unified_diff(expected_data.split('\n'),
   ...                             got.split('\n'))
   >>> list(diff)
   []
