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
"""Convert MS words doc documents to XHTML using OOo and tidy.
"""
import os
from os.path import dirname, join, abspath
from Products.PortalTransforms.interfaces import itransform
from psj.policy.transforms.cmd_oooconv import Document

class Doc2Html(object):
    """A transformation from MS word docs to HTML.
    """
    __implements__ = itransform   # XXX this is Zope2 like ``itransform``

    inputs = (
        'application/msword',
        'application/vnd.openxmlformats-officedocument' +
        '.wordprocessingml.document',
        )
    output = 'text/html'
    output_encoding = 'utf-8'

    def name(self, name=None):
        """Return the name of the transform instance

        The second parameter is only here to satisfy the interface
        requirements, which seem to be broken.
        """
        return 'doc_to_html'

    def convert(self, data, cache, filename=None, mimetype=None, **kwargs):
        """Convert the data, store the result in idata and return that.
        """
        extension = '.doc'
        if mimetype is not None:
            if mimetype == self.inputs[1]:
                extension = '.docx'
        filename = filename or 'unknown' + extension
        if not os.path.splitext(filename.lower())[1] in ['.doc', '.docx']:
            filename += extension
        document = Document(filename, data)
        html = document.convert()
        sub_objects_paths = [document.tmpdir,
                             os.path.join(document.tmpdir, 'Pictures')]
        for path in sub_objects_paths:
            if os.path.exists(path):
                spath, images = document.subObjects(path)
                objects = {}
                if images:
                    document.fixImages(spath, images, objects)
        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

def register():
    return Doc2Html()