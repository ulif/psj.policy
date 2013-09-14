# Tests for the odt_to_html module
import os
import tempfile
import shutil
import unittest
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.data import datastream
from zope.interface.verify import verifyObject, verifyClass
from psj.policy.testing import IntegrationTestCase
from psj.policy.transforms.doc_to_pdf import Doc2Pdf, register


class HelperTests(unittest.TestCase):
    # Tests for non-Doc2Pdf components in module

    def test_register(self):
        # there is a register function that returns an appropriate object
        assert isinstance(register(), Doc2Pdf)


class Doc2PdfTests(unittest.TestCase):
    # Tests for Doc2Pdf class

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.inputdir = os.path.join(os.path.dirname(__file__), 'input')
        self.src_path1 = os.path.join(self.workdir, 'sample1.doc')
        self.src_path2 = os.path.join(self.workdir, 'sample2.docx')
        shutil.copy2(
            os.path.join(self.inputdir, 'testdoc1.doc'), self.src_path1)
        shutil.copy2(
            os.path.join(self.inputdir, 'testdoc1.docx'), self.src_path2)

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_iface(self):
        # make sure we fullfill interface contracts
        obj = Doc2Pdf()
        verifyClass(ITransform, Doc2Pdf)
        verifyObject(ITransform, obj)

    def test_mimetypes(self):
        # we have proper mimetypes set
        transform = Doc2Pdf()
        self.assertEqual(transform.output, 'application/pdf')
        self.assertEqual(transform.output_encoding, 'utf-8')
        self.assertEqual(
            transform.inputs,
            ('application/msword',
             'application/vnd.openxmlformats-officedocument' +
             '.wordprocessingml.document'))

    def test_name(self):
        # we can get the transform name
        transform = Doc2Pdf()
        self.assertEqual(transform.name(), 'doc_to_pdf')
        self.assertEqual(transform.name('other_name'), 'doc_to_pdf')

    def test_cache_dir(self):
        # we can set/get a cache dir
        transform = Doc2Pdf(cache_dir='/foo')
        self.assertEqual(transform.cache_dir, '/foo')

    def test_cache_dir_default(self):
        # we have a cache_dir default (emtpy string)
        transform = Doc2Pdf()
        self.assertEqual(transform.cache_dir, '')

    def test_convert(self):
        # we can convert odt docs to HTML.
        transform = Doc2Pdf()
        idatastream = datastream('mystream')
        transform.convert(
            open(self.src_path2, 'r').read(),
            idatastream)
        self.assertEqual(idatastream.getData()[:7], '%PDF-1.')


class Doc2PdfIntegrationTests(IntegrationTestCase):

    def test_registered(self):
        # the transform is registered in a standard plonesite after install
        transforms = self.portal.portal_transforms
        assert 'doc_to_pdf' in transforms.keys()
