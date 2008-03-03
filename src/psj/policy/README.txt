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

