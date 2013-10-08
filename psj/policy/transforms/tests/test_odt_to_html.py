# Tests for the odt_to_html module
import os
import tempfile
import shutil
import unittest
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.data import datastream
from zope.interface.verify import verifyObject, verifyClass
from psj.policy.testing import IntegrationTestCase
from psj.policy.transforms.odt_to_html import Odt2Html, register


class HelperTests(unittest.TestCase):
    # Tests for non-Odt2Html components in module

    def test_register(self):
        # there is a register function that returns an appropriate object
        assert isinstance(register(), Odt2Html)


class Odt2HtmlTests(unittest.TestCase):
    # Tests for Odt2Html class

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.inputdir = os.path.join(os.path.dirname(__file__), 'input')
        self.src_path1 = os.path.join(self.workdir, 'sample1.odt')
        self.src_path2 = os.path.join(self.workdir, 'sample2.odt')
        shutil.copy2(
            os.path.join(self.inputdir, 'testdoc1.odt'), self.src_path1)
        shutil.copy2(
            os.path.join(self.inputdir, 'testdoc2.odt'), self.src_path2)

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_iface(self):
        # make sure we fullfill interface contracts
        obj = Odt2Html()
        verifyClass(ITransform, Odt2Html)
        verifyObject(ITransform, obj)

    def test_mimetypes(self):
        # we have proper mimetypes set
        transform = Odt2Html()
        self.assertEqual(transform.output, 'text/html')
        self.assertEqual(transform.output_encoding, 'utf-8')
        self.assertEqual(transform.inputs,
                         ('application/vnd.oasis.opendocument.text',))

    def test_name(self):
        # we can get the transform name
        transform = Odt2Html()
        self.assertEqual(transform.name(), 'odt_to_html')
        self.assertEqual(transform.name('other_name'), 'odt_to_html')

    def test_cache_dir(self):
        # we can set/get a cache dir
        transform = Odt2Html(cache_dir='/foo')
        self.assertEqual(transform.cache_dir, '/foo')

    def test_cache_dir_default(self):
        # we have a cache_dir default (emtpy string)
        transform = Odt2Html()
        self.assertEqual(transform.cache_dir, '')

    def test_convert(self):
        # we can convert odt docs to HTML.
        transform = Odt2Html()
        idatastream = datastream('mystream')
        transform.convert(
            open(self.src_path2, 'r').read(),
            idatastream)
        assert '</span>' in idatastream.getData()
        self.assertEqual(idatastream.getMetadata(), {'cache_key_html': None})


class Odt2HtmlIntegrationTests(IntegrationTestCase):

    def test_registered(self):
        # the transform is registered in a standard plonesite after install
        transforms = self.portal.portal_transforms
        assert 'odt_to_html' in transforms.keys()
