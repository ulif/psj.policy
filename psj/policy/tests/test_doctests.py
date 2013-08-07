# tests for psj.policy

import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from zope.component import queryUtility, adapts, provideAdapter
from zope.interface import implements
from zope.schema.interfaces import WrongType
ptc.setupPloneSite()

import psj.policy

class FunctionalTestCase(ptc.FunctionalTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(psj.policy)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

def test_suite():
    suite = unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='psj.content',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='psj.content.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='psj.policy',
        #    test_class=TestCase),

        ztc.FunctionalDocFileSuite(
            'README.txt', package='psj.policy',
            test_class=FunctionalTestCase),

        ])
    return suite
