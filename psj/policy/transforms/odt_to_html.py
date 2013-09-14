##
## odt_to_html.py
##
## Copyright (C) 2008, 2013 Uli Fouquet
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
import os
from os.path import dirname, join, abspath
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from psj.policy.transforms import OOOTransformBase
from psj.policy.transforms.cmd_oooconv import Document


class Odt2Html(OOOTransformBase):
    """A transformation from OpenOffice docs to HTML.
    """
    implements(ITransform)

    inputs = ('application/vnd.oasis.opendocument.text',)
    output = 'text/html'
    output_encoding = 'utf-8'

    def name(self, name=None):
        """Return the name of the transform instance

        The second parameter is only here to satisfy the interface
        requirements, which seem to be broken.
        """
        return 'odt_to_html'

    def convert(self, data, cache, filename=None, **kwargs):
        """Convert the data, store the result in idata and return that.
        """
        filename = filename or 'unknown.odt'
        if not filename.lower().endswith('.odt'):
            filename += '.odt'
        cache_dir = self.cache_dir or None
        document = Document(filename, data, cache_dir=cache_dir)
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
    return Odt2Html()
