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
from os.path import isdir, dirname, join, abspath, splitext
from StringIO import StringIO

from Products.PortalTransforms.libtransforms.commandtransform import (
    commandtransform,)
from Products.PortalTransforms.libtransforms.utils import sansext
from ulif.openoffice.client import PyUNOServerClient

client = PyUNOServerClient()
ooo_convert = client

# This RE finds all text in between SDFIELD tags, even if more than
# one appears in one line...
SDFIELD_RE = re.compile(r'<SDFIELD[^>]*>((.(?!<SDFIELD))*)</SDFIELD>')


class Document(commandtransform):
    """A document that can be unzipped and processed with lxml.
    """

    def __init__(self, name, data):
        """Initialize document.

        Create a temporary directory for conversion.
        """
        self.orig_data = data
        commandtransform.__init__(self, name)
        name = self.name()
        self.tmpdir, self.fullname = self.initialize_tmpdir(
            data, filename=name)

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
        """Convert the document.
        """
        name = self.name()

        response = ooo_convert.convertToHTML(
            filename=name, data=self.orig_data)
        newdir = os.path.dirname(response.message)
        status = response.status
        htmlfilepath = response.message
        if response.status != 200:
            raise IOError('Could not convert: %s' % name)

        # Copy the source file to new location...
        try:
            shutil.copy2(os.path.join(self.tmpdir, name),
                         os.path.join(newdir, name))
        except:
            # No source?
            pass

        # Clean up the HTML code...
        self.tidy(htmlfilepath)
        html = open(htmlfilepath, 'r').read()

        # Remove old tempdir...
        self.cleanDir(self.tmpdir)
        self.tmpdir = newdir
        return html

    def convertToPDF(self):
        name = self.name()
        curr_path = None
        fullpath = os.path.join(self.tmpdir, name)
        result = ooo_convert.convertFileToPDF(path=fullpath)
        if result.status != 200:
            raise IOError('Could not convert: %s' % name)
        pdffilepath = result.message
        pdf = open(pdffilepath, 'r').read()

        # Remove temporary dir...
        shutil.rmtree(os.path.dirname(pdffilepath))
        return pdf

    def tidy(self, filepath):
        """Run tidy over HTML output can produce clean XHTML.

        XXX Generate log msg if tidy fails.
        """
        # tidy does not cope with unknown tags.
        self.stripSdfieldTags(filepath)
        cmd = 'tidy -asxhtml -q -i -n -utf8 -m -f /dev/null %s' % filepath
        os.system(cmd)
        return

    def getMarker(self, tag):
        """Create a marker out of attributes of a string.

        This is a helper for `stripSdfieldTags`, where we replace
        SDFIELD tags by appropriate divs. The divs need a class
        attribute to differentiate between them, for example to differ
        a title tag from an author tag. The name of this class
        attribute is constructed here, be concatenating the values of
        all SDFIELD attributes.

        Example: '<SDFIELD foo=name bar=baz>Value</SDFIELD>'
                 becomes
                 'namebaz'
                 which in the calling function will lead to
                 '<div class='namebaz'>Value</div>'
        """
        attrs = re.findall('[\w]+=[\w]+', tag)
        marker = ''.join([x.lower().split('=')[1] for x in attrs])
        return marker

    def stripSdfieldTags(self, filepath):
        """Strip 'sdfield' tags from file in filepath.

        HTML files generated by OOo might contain SDFIELD tags, which
        stop tidy from working. They are stripped here.
        """
        tmp_fd, outfilepath = tempfile.mkstemp()
        outfile = os.fdopen(tmp_fd, 'w+b')
        for line in open(filepath, 'rb'):
            tags = re.findall('((<SDFIELD[^>]+>)([^<]+)</SDFIELD>)', line)
            if not tags:
                outfile.write(line)
                continue
            for tag in tags:
                marker = self.getMarker(tag[1])
                replacement = '<div class="%s">%s</div>' % (marker, tag[2])
                line = line.replace(tag[0], replacement)
                # Remove embracing <P> tags...
                line = re.sub('<P[^>]+>(<div .*>.*</div>)</P>', r'\1', line)
            outfile.write(line)

        # Copy file back to origin...
        outfile.seek(0)
        open(filepath, 'wb').write(outfile.read())

        outfile.close()
        os.remove(outfilepath)
        return
