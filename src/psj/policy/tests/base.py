##
## base.py
## Login : <uli@pu.smp.net>
## Started on  Thu Feb 28 19:26:38 2008 Uli Fouquet
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
from Products.Five import zcml, fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_psj_policy():
    fiveconfigure.debug_mode = True
    import psj.policy
    zcml.load_config('configure.zcml', psj.policy)
    fiveconfigure.debug_mode = False

    ztc.installPackage('psj.policy')

setup_psj_policy()
ptc.setupPloneSite(products=['psj.policy'])
class PSJPolicyTestCase(ptc.PloneTestCase):
    """
    """
    pass


