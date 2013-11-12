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
import cssutils
import logging
import os
from bs4 import BeautifulSoup
from cStringIO import StringIO
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

    supported_extensions = ['.html', '.xhtml']

    def process(self, path, metadata):
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
        ext = os.path.splitext(path)[1]
        if ext not in self.supported_extensions:
            return path, metadata
        return path, metadata

    def get_css(self, dir_path):
        """Get all paths of CSS files in `dir_path`.

        `dir_path` is the path to some existing directory.

        Returns an iterator over all CSS files with full path.
        """
        for name in sorted(os.listdir(dir_path)):
            if name.endswith('.css'):
                yield os.path.join(dir_path, name)

    def fix_css(self, css_code):
        """Fix CSS code in `css_code`.

        'Fixing' here means to

        - drop CSS selectors not referring to basic style sheet
          selectors (like ``@page``, etc.)

        - modifying remaining selectors by prepending ``#psj-doc ``
          inside. This way all passed-in style sheet rules should
          apply to ``#psj-doc`` marked blocks only (and not to all
          elements in an HTML document).

        - change any `body` selector to select ``#psj-doc`` only.

        Returns the changed CSS code and a string containing any
        warnings.
        """
        if isinstance(css_code, list) or isinstance(css_code, tuple):
            css_code = '\n'.join(css_code)
        logger = logging.getLogger()
        logger.addHandler(logging.NullHandler())
        cssutils.log.setLog(logger)  # ignore warnings
        cssutils.ser.prefs.useDefaults()
        cssutils.ser.prefs.useMinified()

        sheet = cssutils.parseString(css_code)
        new_sheet = cssutils.parseString('')  # create a new result sheet

        for rnum, rule in enumerate(sheet.cssRules):
            if not rule.typeString == 'STYLE_RULE':
                continue  # ignore non-style rules
            for snum, selector in enumerate(rule.selectorList):
                new_selector_text = '#psj-doc %s' % selector.selectorText
                new_selector_text = new_selector_text.replace(' body', '')
                rule.selectorList[snum] = cssutils.css.Selector(
                    new_selector_text)
            new_sheet.cssRules.append(rule)
        return new_sheet.cssText

    def fix_html(self, html_code):
        """Change ``<body>`` tag to ``<div id="psj-doc">`` tag.

        Removes all markup not inside ``<body>`` originally.

        So::

          <html><head>foo</head><body>bar</body></html>

        becomes::

          <div id="psj-doc">bar</div>

        which can be used inside another HTML document. To fix styles
        in CSS docs for the new document structure, you can use
        :meth:`fix_css`.
        """
        soup = BeautifulSoup(html_code)
        body = soup.body
        body.name = 'div'
        body['id'] = 'psj-doc'
        return body.prettify() + '\n'
