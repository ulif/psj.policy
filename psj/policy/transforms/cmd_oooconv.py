##
## cmd_oooconv.py
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
"""
Converters using pyuno, i.e. OpenOffice.org in background.

For conversion to XHTML the commandline tool 'tidy' is needed.
"""
import os
import re
import shutil
import tempfile
from os.path import isdir

from Products.PortalTransforms.libtransforms.commandtransform import (
    commandtransform,)
from ulif.openoffice.client import Client


class Document(commandtransform):
    """A document that can be converted via ulif.openoffice client.

    `name` - basename of file

    `data` - (binary) data of file, the file contents
    """
    def __init__(self, name, data, cache_dir=None):
        commandtransform.__init__(self, name)
        name = self.name()
        self.tmpdir, self.fullname = self.initialize_tmpdir(
            data, filename=name)
        self.cache_dir = cache_dir
        self.client = Client(cache_dir=cache_dir)

    def __del__(self):
        """Remove the temporary directory and loop on all base
        destructors.

        This method is protected against diamond inheritance.
        """
        if isdir(self.tmpdir):
            self.cleanDir(self.tmpdir)
        basekeys = []
        for base in self.__class__.__bases__:
            basekey = str(base)
            if basekey in basekeys:
                continue
            basekeys.append(basekey)
            if hasattr(base, '__del__'):
                base.__del__(self)

    def convert(self):
        """Convert the document to HTML.

        Returns the main document content as string. Additional
        documents (images, etc.) which are result of the conversion
        are placed in the `tmpdir` of this `Document`.

        Raises `IOError` if conversion fails.
        """
        name = self.name()
        src_path = os.path.join(self.tmpdir, name)
        # Convert to HTML, new doc will be in resultpath
        resultpath, cache_key, metadata = self.client.convert(
            src_path,
            {'oocp-out-fmt': 'html',
             'meta-procord': 'oocp,tidy,html_cleaner'})
        if metadata['error']:
            descr = metadata.get('error-descr', 'Descr. not avail.')
            raise IOError('Could not convert: %s [%s]' % (name, descr))
        newdir = os.path.dirname(resultpath)
        html = open(resultpath, 'r').read()
        self.cleanDir(self.tmpdir)
        self.tmpdir = newdir
        return html

    def convertToPDF(self):
        """Convert the document to PDF.

        Returns the generated document contents as string.

        Raises `IOError` if conversion fails.
        """
        name = self.name()
        src_path = os.path.join(self.tmpdir, name)
        pdffilepath, cache_key, metadata = self.client.convert(
            src_path,
            {'oocp-out-fmt': 'pdf',
             'oocp-pdf-version': 'yes',
             'meta-procord': 'oocp',
             })
        if metadata['error']:
            descr = metadata.get('error-descr', 'Descr. not avail.')
            raise IOError('Could not convert: %s [%s]' % (name, descr))

        pdf = open(pdffilepath, 'r').read()

        # Remove temporary dir...
        shutil.rmtree(os.path.dirname(pdffilepath))
        return pdf
