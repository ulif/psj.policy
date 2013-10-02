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
from os.path import isdir

from Products.PortalTransforms.libtransforms.commandtransform import (
    commandtransform,)
from ulif.openoffice.client import Client
from ulif.openoffice.helpers import copy_to_secure_location


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

    def convert(self, cache_key=None):
        """Convert the document to HTML.

        Returns the main document content as string and a cache_key
        for quick later retrieval. Additional documents (images, etc.)
        which are result of the conversion are placed in the `tmpdir`
        of this `Document`.

        If `cache_key` is given (and a `cache_dir` set before) we will
        lookup the cache before performing any real conversion.

        Raises `IOError` if conversion fails.
        """
        name = self.name()
        src_path = os.path.join(self.tmpdir, name)
        options =  {'oocp-out-fmt': 'html',
                    'meta-procord': 'oocp,tidy,html_cleaner,psj_html'}
        resultpath = self.client.get_cached(cache_key)
        if resultpath is not None:
            # Lookup cached doc by cache key (fast)
            newdir = copy_to_secure_location(resultpath)
            resultpath = os.path.join(newdir, os.path.basename(resultpath))
        if resultpath is None:
            # Lookup cached doc by source (expensive)
            resultpath, cache_key = self.client.get_cached_by_source(
                src_path, options)
            if resultpath is not None:
                newdir = copy_to_secure_location(resultpath)
                resultpath = os.path.join(newdir, os.path.basename(resultpath))
        if resultpath is None:
            # Convert to HTML, new doc will be in resultpath
            resultpath, cache_key, metadata = self.client.convert(
                src_path, options)
            if metadata['error']:
                descr = metadata.get('error-descr', 'Descr. not avail.')
                raise IOError('Could not convert: %s [%s]' % (name, descr))
            newdir = os.path.dirname(resultpath)
        html = open(resultpath, 'r').read()
        self.cleanDir(self.tmpdir)
        self.tmpdir = newdir
        return html, cache_key

    def convertToPDF(self, cache_key=None):
        """Convert the document to PDF.

        Returns the generated document contents as string and a cache
        key. The cache_key might be None if no cache_dir was set
        before.

        If `cache_key` is given (and a `cache_dir` set before) we will
        lookup the cache before performing any real conversion.

        Raises `IOError` if conversion fails.
        """
        pdffilepath = self.client.get_cached(cache_key)
        if pdffilepath is not None:
            return open(pdffilepath, 'r').read(), cache_key
        name = self.name()
        src_path = os.path.join(self.tmpdir, name)
        options = {
            'oocp-out-fmt': 'pdf',
            'oocp-pdf-version': 'yes',
            'meta-procord': 'oocp',
            }
        pdffilepath, cache_key = self.client.get_cached_by_source(
            src_path, options)
        if pdffilepath is not None:
            return open(pdffilepath, 'r').read(), cache_key
        pdffilepath, cache_key, metadata = self.client.convert(
            src_path, options)
        if metadata['error']:
            descr = metadata.get('error-descr', 'Descr. not avail.')
            raise IOError('Could not convert: %s [%s]' % (name, descr))
        pdf = open(pdffilepath, 'r').read()

        # Remove temporary dir...
        self.tmpdir = os.path.dirname(pdffilepath)
        self.cleanDir(self.tmpdir)
        return pdf, cache_key
