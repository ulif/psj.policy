##
## odt_to_html.py
## Login : <uli@pu.smp.net>
## Started on  Thu Mar  6 10:26:50 2008 Uli Fouquet
## $Id$
## 
## Copyright (C) 2008 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
from Products.PortalTransforms.interfaces import itransform

class Odt2Html(object):
    """A transformation from OpenOffice docs to HTML.
    """
    __implements__ = itransform   # XXX this is Zope2 like ``itransform``

    def name(self, name=None):
        """Return the name of the transform instance

        The second parameter is only here to satisfy the interface
        requirements, which seem to be broken.
        """
        return 'odt_to_html'

    def convert(self, data, cache, filename=None, **kwargs):
        """Convert the data, store the result in idata and return that.
        """
        pass

def register():
    return Odt2Html()
