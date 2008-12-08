*******************************************
psj.policy -- A policy for Perpectiva sites
*******************************************

:Test-Layer: integration

The site properties
===================

The policy sets some default properties for newly created Perspectivia
sites. Another default site name is set::

   >>> self.portal.getProperty('title')
   'Perspectivia Site'

Also a different default description is set::

   >>> self.portal.getProperty('description')
   'Welcome to Perspectivia!'

The special transforms
======================

This package defines some special transforms::

   >>> from psj.policy.transforms import odt_to_html

   >>> from Products.CMFCore.utils import getToolByName
   >>> transforms = self.portal.portal_transforms
   >>> transforms
   <TransformTool at /plone/portal_transforms>

The transform tool maintains a list of tuples, each one describing a
single transformation.


The .odt to .html transform
---------------------------

We pick the .odt to HTML transformation, which
should be registered during startup::

   >>> odt_trans_name, odt_transform =  [x for x in transforms.items() 
   ...                                   if x[0] == 'odt_to_html'][0]
   >>> odt_transform
   <Transform at /plone/portal_transforms/odt_to_html>

This transform supports one input MIME type::

   >>> odt_transform.inputs
   ('application/vnd.oasis.opendocument.text',)

It delivers text/html::

   >>> odt_transform.output
   'text/html'


The .odt to .pdf transform
--------------------------

The trasformation from OOo .odt files to PDF should also be available
after startup::

   >>> odt_trans_name, odt_transform =  [x for x in transforms.items() 
   ...                                   if x[0] == 'odt_to_pdf'][0]
   >>> odt_transform
   <Transform at /plone/portal_transforms/odt_to_pdf>

This transform supports one input MIME type::

   >>> odt_transform.inputs
   ('application/vnd.oasis.opendocument.text',)

It delivers a pdf document::

   >>> odt_transform.output
   'application/pdf'

This transform should be picked up by the machinery by default, when
we want to get a PDF representation of an .odt file::

   >>> t = transforms._findPath(
   ...        'application/vnd.oasis.opendocument.text', 
   ...        'application/pdf')[0]
   >>> t
   <Transform at odt_to_pdf>

Now let's get a real file an let it be transformed::

   >>> import os
   >>> testfilepath = os.path.dirname(os.path.abspath(__file__))
   >>> testfilepath = os.path.join(testfilepath, 'transforms', 'tests',
   ...                             'input')
   >>> odtfilepath = os.path.join(testfilepath, 'testdoc1.odt')
   >>> doc = open(odtfilepath, 'rb').read()

We run the transform by calling the portal tools::

   >>> data = transforms.convertTo(
   ...     'application/pdf', doc,
   ...     mimetype='application/vnd.oasis.opendocument.text')
   >>> pdf = data.getData()
   >>> print pdf[:10]
   %PDF-1.4...

   

The .doc to .html transform
---------------------------

We pick the .odt to HTML transformation, which
should be registered during startup::

   >>> doc_trans_name, doc_transform =  [x for x in transforms.items() 
   ...                                   if x[0] == 'doc_to_html'][0]
   >>> doc_transform
   <Transform at /plone/portal_transforms/doc_to_html>

This transform supports one input MIME type::

   >>> doc_transform.inputs
   ('application/msword',)

It delivers text/html::

   >>> doc_transform.output
   'text/html'

The local doc transform should picked by default, if something has to
be converted from application/msword to text/html::

   >>> t = transforms._findPath('application/msword', 'text/html')[0]
   >>> t
   <Transform at doc_to_html>

But 'word_to_html' should be still available, in case our extension is
unregistered::

   >>> 'word_to_html' in transforms.keys()
   True

We grab a simple
doc file from the tests directory in `transforms`::

   >>> import os
   >>> testfilepath = os.path.dirname(os.path.abspath(__file__))
   >>> testfilepath = os.path.join(testfilepath, 'transforms', 'tests',
   ...                             'input')
   >>> docfilepath = os.path.join(testfilepath, 'simpledoc1.doc')
   >>> doc = open(docfilepath, 'rb').read()

Now we let the portal transforms transform this document::

   >>> data = transforms.convertTo('text/html', doc,
   ...                             mimetype='application/msword')
   >>> html = data.getData()
   >>> print html
   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   ...A simple document...
   </html>


The .doc to .pdf transform
--------------------------

The trasformation from MS .doc files to PDF should also be available
after startup::

   >>> doc_trans_name, doc_transform =  [x for x in transforms.items() 
   ...                                   if x[0] == 'doc_to_pdf'][0]
   >>> doc_transform
   <Transform at /plone/portal_transforms/doc_to_pdf>

This transform supports one input MIME type::

   >>> doc_transform.inputs
   ('application/msword',)

It delivers a pdf document::

   >>> doc_transform.output
   'application/pdf'

This transform should be picked up by the machinery by default, when
we want to get a PDF representation of an .odt file::

   >>> t = transforms._findPath(
   ...        'application/msword', 
   ...        'application/pdf')[0]
   >>> t
   <Transform at doc_to_pdf>

Now let's get a real file an let it be transformed::

   >>> import os
   >>> testfilepath = os.path.dirname(os.path.abspath(__file__))
   >>> testfilepath = os.path.join(testfilepath, 'transforms', 'tests',
   ...                             'input')
   >>> docfilepath = os.path.join(testfilepath, 'testdoc1.doc')
   >>> doc = open(docfilepath, 'rb').read()

We run the transform by calling the portal tools::

   >>> data = transforms.convertTo(
   ...     'application/pdf', doc,
   ...     mimetype='application/msword')
   >>> pdf = data.getData()
   >>> print pdf[:10]
   %PDF-1.4...
