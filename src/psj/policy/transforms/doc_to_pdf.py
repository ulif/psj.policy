##
## doc_to_html.py
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
"""Convert MS words doc documents to PDF using OOo.
"""
import os
from os.path import dirname, join, abspath
from Products.PortalTransforms.interfaces import itransform
from psj.policy.transforms.cmd_oooconv import Document

class Doc2Pdf(object):
    """A transformation from MS word docs to PDF.

    Supports .doc and .docx.
    """
    __implements__ = itransform   # XXX this is Zope2 like ``itransform``

    inputs = (
        'application/msword',
        'application/vnd.openxmlformats-officedocument' +
        '.wordprocessingml.document',)
    output = 'application/pdf'
    output_encoding = 'utf-8'

    def name(self, name=None):
        """Return the name of the transform instance

        The second parameter is only here to satisfy the interface
        requirements, which seem to be broken.
        """
        return 'doc_to_pdf'

    def convert(self, data, cache, filename=None, mimetype=None, **kwargs):
        """Convert the data, store the result in idata and return that.
        """
        extension = '.doc'
        if mimetype is not None:
            if mimetype == self.inputs[1]:
                extension = '.docx'
        filename = filename or 'unknown' + extension
        if not (filename.lower().endswith('.doc') or
                filename.lower().endswith('.docx')):
            filename += extension
        document = Document(filename, data)
        pdf = document.convertToPDF()
        cache.setData(pdf)
        return cache

def register():
    return Doc2Pdf()
