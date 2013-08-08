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



from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting

from plone.testing import z2

class PSJPolicyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import psj.policy
        self.loadZCML(package=psj.policy)

        # Install product and call its initialize() function
        z2.installProduct(app, 'psj.policy')

        # Note: you can skip this if my.product is not a Zope 2-style
        # product, i.e. it is not in the Products.* namespace and it
        # does not have a <five:registerPackage /> directive in its
        # configure.zcml.

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'psj.policy:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'psj.policy')

        # Note: Again, you can skip this if my.product is not a Zope 2-
        # style product

MY_PRODUCT_FIXTURE = PSJPolicyLayer()
MY_PRODUCT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MY_PRODUCT_FIXTURE,), name="PSJPolicy:Integration")
MY_PRODUCT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MY_PRODUCT_FIXTURE,), name="PSJPolicy:Functional")

class IntegrationTestCase(unittest.TestCase):

    layer = MY_PRODUCT_INTEGRATION_TESTING

class FunctionalTestCase(unittest.TestCase):

    layer = MY_PRODUCT_FUNCTIONAL_TESTING

    @property
    def portal(self):
        return self.layer['portal']


class DISFunctionalTestCase(ptc.FunctionalTestCase):

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
