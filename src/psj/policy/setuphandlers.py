##
## setuphandlers.py
## Login : <uli@pu.smp.net>
## Started on  Mon Mar 10 03:42:33 2008 Uli Fouquet
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
"""Setup psj extensions.
"""

import mimetypes
from Products.CMFCore.utils import getToolByName
import transaction

from StringIO import StringIO
from types import InstanceType
from psj.policy import logger

PRODUCT_DEPENDENCIES = ()

new_mimetypes = (
    {
        'name': 'Office Word 2007 XML document',
        'mimetypes': (
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',),
        'extensions': ('docx',)
        },
    )

for mt in new_mimetypes:
    mt['globs'] = tuple(['*.' + ext for ext in mt['extensions']])
    mt['icon_path'] = '++resource++psjpolicy-icons/%s.png' % mt['extensions'][0]
    # Adding to standard mimetypes
    mimetypes.add_type(mt['mimetypes'][0], '.' + mt['extensions'][0])

del mimetypes


    
def registerTransform(site, out, name, module):
    transforms = getToolByName(site, 'portal_transforms')
    try:
        transforms.manage_addTransform(name, module)
        print >> out, "Registered transform", name
    except:
        print >> out, "Transform %s already registered. Try reregister." % name
        try:
            transforms.unregisterTransform(name)
            transforms.manage_addTransform(name, module)
        except KeyError:
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print "WARNING!"
            print "The %s transform could not be installed!" % name
            print "Try registering it manually!"
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        pass


def unregisterTransform(site, out, name):
    transforms = getToolByName(site, 'portal_transforms')
    try:
        transforms.unregisterTransform(name)
        print >> out, "Removed transform", name
    except AttributeError:
        print >> out, "Could not remove transform", name, "(not found)"

def register_products(site, out, reinstall=False):
    quickinstaller = getToolByName(site, 'portal_quickinstaller')
    for product in PRODUCT_DEPENDENCIES:
        if reinstall and quickinstaller.isProductInstalled(product):
            quickinstaller.reinstallProducts([product])
            transaction.savepoint()
        elif not quickinstaller.isProductInstalled(product):
            quickinstaller.installProducts([product])
            transaction.savepoint()
    return

def register_mime_type(site, mime_type_reg, out, mt_dict):
    main_mt = mt_dict['mimetypes'][0]
    mt_name = mt_dict['name']
    if bool(mime_type_reg.lookup(main_mt)):
        # Already installed
        logger.info(
            "%s (%s) Mime type already installed, skipped",
            main_mt, mt_name)
        return 
    mime_type_reg.manage_addMimeType(
        mt_name,
        mt_dict['mimetypes'],
        mt_dict['extensions'],
        mt_dict['icon_path'],
        binary=True,
        globs=mt_dict['globs'])
    logger.info("%s (%s) Mime type installed", main_mt, mt_name)

    
def install(site):
    """Install psj stuff.
    """
    out = StringIO()

    # Register mime-types
    mime_type_reg = getToolByName(site, 'mimetypes_registry')
    for mt_dict in new_mimetypes:
        register_mime_type(site, mime_type_reg, out, mt_dict)
        pass
    
    # Register transforms
    for name, module in [
        ('ooo_html_body', 'psj.policy.transforms.ooo_html_body'),
        ('odt_to_html', 'psj.policy.transforms.odt_to_html'),
        ('odt_to_pdf', 'psj.policy.transforms.odt_to_pdf'),
        ('doc_to_html', 'psj.policy.transforms.doc_to_html'),
        ('doc_to_pdf', 'psj.policy.transforms.doc_to_pdf'),]:
        print >> out, "Installing %s transform" % name
        registerTransform(site, out, name, module)
    # Reregister standard transformations, so that they appear in the
    # list of transforms _after_ ours.
    unregisterTransform(site, out, 'word_to_html')
    registerTransform(site, out, 'word_to_html',
                      'Products.PortalTransforms.transforms.word_to_html')

    # Register additional products
    register_products(site, out)
    return out.getvalue()

def uninstall(site):
    """Uninstall psj stuff.
    """
    out = StringIO()

    # Remove transforms
    unregisterTransform(site, out, 'ooo_html_body')
    unregisterTransform(site, out, 'odt_to_html')
    unregisterTransform(site, out, 'odt_to_pdf')
    unregisterTransform(site, out, 'doc_to_html')
    unregisterTransform(site, out, 'doc_to_pdf')

    # Remove mimetypes
    mime_type_reg = getToolByName(site, 'mimetypes_registry')
    mt_ids = [mt_dict['mimetypes'][0] for mt_dict in new_mimetypes]
    mime_type_reg.manage_delObjects(mt_ids)
   
    return out.getvalue()

def setupPSJTransforms(context):
    """
    Setup PortalTransforms step.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('portal-transforms-various.txt') is None:
        return
    out = []
    site = context.getSite()
    installPSJTransforms(site)

def setupPSJSite(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    #if context.readDataFile('portal-transforms-various.txt') is None:
    #    return
    out = []
    site = context.getSite()
    install(site)
