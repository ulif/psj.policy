import unittest
from Products.Archetypes.tests.atsitetestcase import ATFunctionalSiteTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as FileSuite

DOCTEST_FILES = ('README.txt',)

def test_suite():
    suite = unittest.TestSuite()
    for testfile in DOCTEST_FILES:
        suite.addTest(FileSuite(
            testfile,
            package="psj.policy",
            test_class=ATFunctionalSiteTestCase)
                      )
    return suite
