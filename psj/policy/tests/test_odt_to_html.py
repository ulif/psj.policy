# Tests for transforms/odt_to_html module
import unittest
from Products.PortalTransforms.interfaces import ITransform
from zope.interface.verify import verifyClass, verifyObject
from psj.policy.transforms.odt_to_html import Odt2Html


class Odt2HtmlUnittests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill promised interfaces
        trans = Odt2Html()
        assert verifyClass(ITransform, Odt2Html)
        assert verifyObject(ITransform, trans)

    def test_attributes(self):
        # make sure the transform has attributes set correctly
        trans = Odt2Html()
        self.assertEqual(
            trans.inputs, ('application/vnd.oasis.opendocument.text',))
        self.assertEqual(trans.output, 'text/html')
        self.assertEqual(trans.output_encoding, 'utf-8')
        self.assertEqual(trans.name(), 'odt_to_html')
