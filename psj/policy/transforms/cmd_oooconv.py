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

client = Client()
ooo_convert = client

# This RE finds all text in between SDFIELD tags, even if more than
# one appears in one line...
SDFIELD_RE = re.compile(r'<SDFIELD[^>]*>((.(?!<SDFIELD))*)</SDFIELD>')


class Document(commandtransform):
    """A document that can be converted via ulif.openoffice client.

    `name` - basename of file

    `data` - (binary) data of file, the file contents
    """
    def __init__(self, name, data):
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
        """Convert the document to HTML.

        Returns the main document content as string. Additional
        documents (images, etc.) which are result of the conversion
        are placed in the `tmpdir` of this `Document`.

        Raises `IOError` if conversion fails.
        """
        name = self.name()
        src_path = os.path.join(self.tmpdir, name)
        # Convert to HTML, new doc will be in resultpath
        resultpath, cache_key, metadata = ooo_convert.convert(
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
        pdffilepath, cache_key, metadata = ooo_convert.convert(
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
