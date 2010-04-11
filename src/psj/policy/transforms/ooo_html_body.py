##
## ooo_html_body.py
## Login : <uli@pu.smp.net>
## Started on  Sun Apr 11 16:20:10 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
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
"""Transforms to strip body/header from OO.org generated HTML.
"""
import re
from Products.CMFDefault.utils import bodyfinder
from Products.PortalTransforms.interfaces import itransform
from psj.policy.transforms.cmd_oooconv import Document

class OOoHTMLBody(object):
    """Get body from OO.org generated HTML.

    Returns HTML fragment embedded in ``<div>`` tag. We also add the
    ``CDATA`` defined in header as ``style`` attribute of the topmost
    ``<div>`` tag returned.
    """
    __implements__ = itransform   # XXX this is Zope2 like ``itransform``
    __name__ = 'ooo_html_body'
    
    inputs = ('text/html',)
    output = 'text/html'
    output_encoding = 'utf-8'


    def __init__(self, name=None):
        self.config_metadata = {
            'inputs' : (
                'list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name
    
    def name(self, name=None):
        """Return the name of the transform instance

        The second parameter is only here to satisfy the interface
        requirements, which seem to be broken.
        """
        return self.__name__

    def convert(self, orig, data, **kwargs):
        """Convert the data, store the result in data and return that.
        """
        body = bodyfinder(orig)
        styledef = re.findall(
            'CDATA.*?<!--(.*?)-->', orig, re.S|re.M)[0]
        styledef = styledef.replace('"', "'")
        body = '<div class="ooodocument" style="%s">%s</div>' % (
            styledef, body)
        data.setData(body)
        return data

def register():
    return OOoHTMLBody()
