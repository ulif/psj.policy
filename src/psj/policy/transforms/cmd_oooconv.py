##
## cmd_oooconv.py
## Login : <uli@pu.smp.net>
## Started on  Thu Mar 13 11:57:58 2008 Uli Fouquet
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
from psj.policy.bin import ooo_convert

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
        curr_path = os.getcwd()
        os.chdir(self.tmpdir)
        ooo_convert.convert_to_html(path=name)

        htmlfilepath = os.path.join(
            self.tmpdir, "%s.html" % sansext(name))
        
        self.tidy(htmlfilepath)
        html = open(htmlfilepath, 'r').read()
        os.chdir(curr_path)
        return html

    def convertToPDF(self):
        name = self.name()
        curr_path = os.getcwd()
        os.chdir(self.tmpdir)
        ooo_convert.convert_to_pdf(path=name)
        pdffilepath = os.path.join(
            self.tmpdir, "%s.pdf" % sansext(name))
        pdf = open(pdffilepath, 'r').read()
        os.chdir(curr_path)
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

    def stripSdfieldTags(self, filepath):
        """Strip 'sdfield' tags from file in filepath.

        HTML files generated by OOo might contain SDFIELD tags, which
        stop tidy from working. They are stripped here.
        """
        tmp_fd, outfilepath = tempfile.mkstemp()
        outfile = os.fdopen(tmp_fd, 'w+b')
        for line in open(filepath, 'rb'):
            outfile.write(SDFIELD_RE.sub(r'\1', line))
            
        # Copy file back to origin...
        outfile.seek(0)
        open(filepath, 'wb').write(outfile.read())
        
        outfile.close()
        os.remove(outfilepath)
        return
