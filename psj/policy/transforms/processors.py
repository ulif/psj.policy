##
## processors.py
##
## Copyright (C) 2013 Uli Fouquet
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
ulif.openoffice processors.
"""
from ulif.openoffice.processor import BaseProcessor

class PSJHTMLProcessor(BaseProcessor):
    """A document processor that post-processes HTML generated.

    As other `ulif.openoffice` docuement processors it works like a
    filter that gets some document, modifies it (or not), and returns
    a path to the resulting document.

    The processors' name for use in `ulif.openoffice` pipeline is
    ``psj_html``.
    """
    prefix = 'psj_html'

    def process(self, input_path, metadata):
        """Do PSJ-specific adaptions of generated HTML input.

        `input_path` gives any (beforehand) generated HTML
        document. The path might be located in a directory with
        additional files (images, etc.) that could also be processed.

        `metadata` is a dictionary of metadata concerning the
        conversion process. It contains at least a key ``error`` with
        a boolean value (should alway be `False`, otherwise the
        document conversion failed), and a key ``error-descr`` which
        contains some error message in case of failures.

        The ``error`` and ``error-descr`` should be set when
        unresolvable processing problems occur.

        Returns a tuple (``result_path``, ``metadata``) with
        ``result_path`` containing the path to the modified document
        and ``metadata`` containing the updated ``metadata`` directory
        passed in.
        """
        return input_path, metadata
