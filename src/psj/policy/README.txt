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

