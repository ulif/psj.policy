psj.policy.transforms
*********************

:Author: Uli Fouquet
:Test-Layer: unit

One of the major aims of Plone Scholarly Journal sites is, to process
content, that was delivered in .odt or .docx formats. Transforms are
the Plone way to handle such 'external' document formats.

Currently supported is a set of transformations for XML based document
formats like OpenOffice.orgs `.odt` and Microsofts `.docx`
format. Those formats share the attribute to be in fact zipped XML
files.

The current transformations provided are:

- odt to HTML via lxml.

- odt to HTML via OpenOffice.org (OOo)

- odt to PDF/A via OpenOffice.org (OOo)

- docx to HTML via lxml.

- doc to PDF/A via OpenOffice.org (OOo)

- doc to HTML via OpenOffice.org (OOo)

- docx to HTML via OpenOffice.org (OOo)

- docx to PDF/A via OpenOffice.org (OOo)

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
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ""><html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>Test</title></head><body><h1>Hello!</h1>Blah</body></html>


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
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ...><html xmlns="http://www.w3.org/1999/xhtml">...</html>

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


Create a virtual odt document (with OpenOffice.org)
---------------------------------------------------

The most powerfull method to transforms documents of all kind might be
to use OpenOffice.org (OOo) because here we can use a fully fledged
office suite in the background. We provide a virtual OOo document in
the ``cmd_oooconv`` module::

   >>> from psj.policy.transforms.cmd_oooconv import Document
   >>> document = Document('myodtdoc.odt', content_in)

Convert the virtual document to HTML (using OOo)
------------------------------------------------

   >>> output, cache_key = document.convert()
   >>> output
   '<div ...</div>\n'

Convert the virtual document to PDF/A (using OOo)
-------------------------------------------------

We cannot only convert data to HTML but also to PDF::

XXX
XXX Why do we have to create a new doc each time after convert()?
XXX

   >>> document = Document('myodtdoc', content_in)
   >>> output, cache_key = document.convertToPDF()

The ``output`` variable now contains our PDF document::

   >>> output
   '%PDF-1.4\n%...'

   >>> len(output) > 1100000
   True

while the `cache_key` is not set (we did not set a cache dir)::

   >>> cache_key is None
   True

As you see, PDF/A documents are pretty large, because they store all
related data of the document, especially fonts.

All this is very well, but now we also want OOo documents
automatically to be recognized and handled approprietely.


Converting .doc(x) files with OOo
=================================

There are basically two $MS document types, that we support: .doc and
the newer .docx format. We start with handling the first.

Converting .doc files with OOo
------------------------------

Our OOo helper in ``cmd_oooconv`` provides conversion of documents
to HTML and PDF format. The conversion is done by creating a virtual
document and then calling a specialized convert method. It accepts the
input filetypes, that are provided by OOo. So also .doc documents can
be converted.

To perform this step, a virtual document has to be created first::

   >>> from psj.policy.transforms.cmd_oooconv import Document
   >>> input_file_path = join(input_path, 'testdoc1.doc')
   >>> content_in = r'' + open(input_file_path, 'rb').read()
   >>> document = Document('mydoc1.doc', content_in)

As we can see, the virtual document name can be different from the
original. Now we convert this document to HTML::

   >>> html, cache_key = document.convert()
   >>> print html
   <div dir="ltr" id="psj-doc" lang="de-DE">
   ...
   </div>

Also conversion to PDF/A is possible::

   >>> document = Document('mydoc1.doc', content_in)
   >>> pdf, cache_key = document.convertToPDF()
   >>> pdf[:20]
   '%PDF-1.4\n%...'

   >>> len(pdf) > 1100000
   True

   >>> cache_key is None
   True


Converting .docx files with OOo
------------------------------

Now we care for the newer docx file type, load a sample document and
convert it to HTML::

   >>> input_file_path = join(input_path, 'testdoc1.docx')
   >>> document = Document('mydoc1.docx', content_in)
   >>> html, cache_key = document.convert()
   >>> print html
   <div dir="ltr" id="psj-doc" lang="de-DE">
   ...
   </div>

Converting to PDF is easy as well::

   >>> document = Document('mydoc1.docx', content_in)
   >>> pdf, cache_key = document.convertToPDF()
   >>> pdf[:20]
   '%PDF-1.4\n%...'

   >>> len(pdf) > 1100000
   True

   >>> cache_key is None
   True


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

A transform should alway provide ``itransform``::

   >>> from Products.PortalTransforms.interfaces import itransform
   >>> itransform.providedBy(transform)
   True

   >>> from zope.interface.verify import verifyObject
   >>> verifyObject(itransform, transform)
   True


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

   >>> input_file_path = join(input_path, 'testdoc1.odt')
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
   >>> idatastream.providedBy(res_data)
   True

This stream can be read. We get the data::

   >>> got = res_data.getData()

   >>> print got
   <div dir="ltr" id="psj-doc" lang="de-DE">
   ...
   </div>

There should be no 'HTML encoding' of characters, because users will
search the catalog for 'Äpfel' and not '&Auml;pfel'::

   >>> 'w&uuml;nscht' in got
   False

   >>> 'wünscht' in got
   True


Handle foreign character sets correctly
---------------------------------------

The transformation should also cope with non-standard western
documents. We upload an example with japanese chars.

For this, we again get the raw data from the document::

   >>> input_file_path = join(input_path, 'testdoc2.odt')
   >>> raw_odt = open(input_file_path).read()

Then, we need a new 'datastream', in wich the results will be
stored::

   >>> from Products.PortalTransforms.data import datastream
   >>> data = datastream('odt_to_html')

Now we can perform the real conversion in a transformation context::

   >>> res_data = transform.convert(raw_odt, data,
   ...                              filename='testdoc2.odt')
   >>> got = res_data.getData()

   >>> print got
   <div dir="ltr" id="psj-doc" lang="de-DE" xml:lang="de-DE">
   ...
   </div>

There are real japanese Characters in the document::

   >>> got_u = got.decode('utf-8')
   >>> u'\u304a\u732b\u3055\u307e' in got_u
   True

There are real arabic Characters in the document::

   >>> 'xml:lang="ar-SA">\xd8\xa7\xd9\x84\xd8\xa7\xd8' in got
   True

There are real cyrillic characters in the document::

   >>> '\xd1\x81\xd0\xbc\xd0\xb5\xd1\x8f' in got
   True


Convert .doc to HTML
====================

All this was about odt docs. We now care for another transformation
available with PSJ: the doc conversion. This also uses OOo as
converting engine in background.

All the testfiles we want to compare reside in the ``tests``
subdirectory::

   >>> from os.path import join, dirname
   >>> input_path = join(dirname(__file__), 'tests', 'input')
   >>> output_path = join(dirname(__file__), 'tests', 'output')

First we want to compare two files called ``testdoc1``::

   >>> input_file_path = join(input_path, 'testdoc1.doc')


Create a transformation (doc to HTML)
-------------------------------------

Furthermore, we pick up our transformation. It is defined in the
``doc_to_html`` module, but we get an instance of the real
transformation class by calling ``register()``

   >>> from psj.policy.transforms import doc_to_html
   >>> transform = doc_to_html.register()
   >>> transform
   <psj.policy.transforms.doc_to_html.Doc2Html object at 0x...>

   >>> transform.inputs
   ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

   >>> transform.output
   'text/html'

   >>> transform.output_encoding
   'utf-8'

Perform a transformation
------------------------

For this, we again get the raw data from the document::

   >>> input_file_path = join(input_path, 'testdoc1.doc')
   >>> raw_doc = open(input_file_path).read()

Then, we need a new 'datastream', in wich the results will be
stored::

   >>> from Products.PortalTransforms.data import datastream
   >>> data = datastream('doc_to_html')

Now we can perform the real conversion in a transformation context::

   >>> res_data = transform.convert(raw_doc, data,
   ...                              filename='testdoc1.doc')

This stream can be read. We get the data::

   >>> got = res_data.getData()

   >>> print got
   <div dir="ltr" id="psj-doc" lang="de-DE">
   ...
   </div>

There should be no 'HTML encoding' of characters, because users will
search the catalog for 'Äpfel' and not '&Auml;pfel'::

   >>> 'w&uuml;nscht' in got
   False

   >>> 'wünscht' in got
   True

Create a transformation (doc to PDF)
-------------------------------------

Another available transformation is the one from .doc files to PDF. As
we only support PDF/A, we will get those type back.

The transformation is defined in ``doc_to_pdf`` module, but we get an
instance of the real transformation class by calling ``register()``

   >>> from psj.policy.transforms import doc_to_pdf
   >>> transform = doc_to_pdf.register()
   >>> transform
   <psj.policy.transforms.doc_to_pdf.Doc2Pdf object at 0x...>

   >>> transform.inputs
   ('application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

   >>> transform.output
   'application/pdf'

We grab a testdocument again to transform it::

   >>> input_file_path = join(input_path, 'testdoc1.doc')
   >>> raw_doc = open(input_file_path).read()

Then, we need a new 'datastream', in wich the results will be
stored::

   >>> from Products.PortalTransforms.data import datastream
   >>> data = datastream('doc_to_pdf')

Now we can perform the real conversion in a transformation context::

   >>> res_data = transform.convert(raw_doc, data, 
   ...                              filename='testdoc1.doc')

This stream can be read. We get the data::

   >>> got = res_data.getData()
   >>> print got[:10]
   %PDF-1.4
   ...
