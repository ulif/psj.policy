##
## prepare.py
## Login : <uli@pu.smp.net>
## Started on  Fri Apr  4 02:15:53 2008 Uli Fouquet
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
"""Prepare a PSJ installation.

Usage: python <scriptname> [--restore]

- Move xslt and xml2 libs from local openoffice install to backup directory.

- Run `ldconfig <path-to-OOo-dir`

If `--restore` is given, the libloader will be restored.

"""
import os
import sys
import shutil

OOO_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OOO_PATH = os.path.join(OOO_PATH, 'parts', 'openoffice', 'program')
BACKUP_PATH = os.path.join(OOO_PATH, '_backups')

def check_permissions():
    if not sys.platform.startswith('linux'):
        print "This script only runs on Linux platform."
        sys.exit(1)

    if os.geteuid() != 0:
        print "You must be root to run this script."
        sys.exit(1)
    

def prepare():
    """Move libxslt and libxml to backupdir and run ldconfig.
    """
    check_permissions()
    
    file_list = os.listdir(OOO_PATH)
    
    print "Moving xslt and xml2 libs from local openoffice install..."
    if not os.path.isdir(BACKUP_PATH):
        os.mkdir(BACKUP_PATH)

    file_list = [x for x in file_list
                 if x.startswith('libxslt.so') or x.startswith('libxml2.so')]
    for name in file_list:
        src = os.path.join(OOO_PATH, name)
        dst = os.path.join(BACKUP_PATH, name)
        shutil.copy2(src, dst)
        os.remove(src)
        print "  Moved %s to %s" % (src, dst)

    cmd = "ldconfig %s" % OOO_PATH
    print "Running %s to load OOo libs." % cmd
    os.system(cmd)

    print "Done."


def restore():
    check_permissions()
    cmd = "ldconfig"
    print "Running ldconfig w/o args to restore libloader."
    os.system(cmd)

    print "Done."


def main(argv=sys.argv):

    if len(argv) > 1 and argv[1] == '--restore':
        restore()
        sys.exit(0)

    prepare()

if __name__ == '__main__':
    main()
