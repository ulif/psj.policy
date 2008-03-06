##
## prog_xsltproc.py
## Login : <uli@pu.smp.net>
## Started on  Thu Mar  6 10:35:07 2008 Uli Fouquet
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
Converters powered by the external xsltproc helper.
"""
from os.path import isdir
from Products.PortalTransforms.libtransforms.commandtransform import (
    commandtransform,)



class Document(commandtransform):
    """A document that can be processed with xsltproc.
    """
    def __init__(self, name, data):
        """Initialize document.

        Append '.odt' to filename if missing and create a temporary
        directory for conversion.
        """
        commandtransform.__init__(self, name, binary='xsltproc')
        name = self.name()
        if not name.lower().endswith('.odt'):
            name = name + '.odt'
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
