# tests for cmd_oooconv module
import os
import shutil
import tempfile
import unittest
from psj.policy.transforms.cmd_oooconv import Document
from Products.PortalTransforms.data import datastream


class DocumentTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        input_dir = os.path.join(os.path.dirname(__file__), 'input')
        self.doc_simple1_path = os.path.join(input_dir, 'simpledoc1.doc')
        self.doc_simple1 = open(self.doc_simple1_path, 'rb').read()
        self.idata = datastream('mytestdoc.doc')
        self.idata.setData(self.doc_simple1)
        self.doc = None   # to be set by tests

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_attribs(self):
        # Documents have some attributes, notably a tmpdir and a fullpath
        self.doc = Document('mytestdoc.doc', self.doc_simple1)
        assert self.doc.tmpdir is not None
        assert self.doc.fullname[-14:] == '/mytestdoc.doc'
        assert self.doc.cache_dir is None

    def test_del_removes_tmp_dir(self):
        # Deleted `Document`s do not leave any temp dirs
        self.doc = Document('mytestdoc.doc', self.doc_simple1)
        path = self.doc.fullname
        assert os.path.isfile(path)
        del self.doc
        assert not os.path.isfile(path)

    def test_convert(self):
        # We can convert docs to HTML
        self.doc = Document('mytestdoc.doc', self.doc_simple1)
        html, cache_key = self.doc.convert()
        assert 'A simple document.</p>' in html
        # no cache_dir, no cached doc
        assert cache_key is None

    def test_convert_w_cache_dir(self):
        # We can cache after converting
        self.doc = Document('mytestdoc.doc', self.doc_simple1, self.workdir)
        html, cache_key = self.doc.convert()
        assert 'A simple document.</p>' in html
        self.assertEqual(cache_key, 'cc8c3b702ca3865608732f612691978b_1_1')

    def test_convert_w_cache_key(self):
        # Cached docs are retrieved
        self.doc = Document('mytestdoc.doc', self.doc_simple1, self.workdir)
        html1, cache_key1 = self.doc.convert()  # store doc in cache
        html2, cache_key2 = self.doc.convert(cache_key=cache_key1)
        assert html1 == html2
        assert cache_key1 == cache_key2

    def test_convert_to_pdf(self):
        # We can convert docs to PDF
        self.doc = Document('mytestdoc.doc', self.doc_simple1)
        pdf, cache_key = self.doc.convertToPDF()
        self.assertEqual(pdf[:6], '%PDF-1')
        # no cache_dir, no cached doc
        assert cache_key is None

    def test_convert_to_pdf_w_cache_dir(self):
        # We can cache after converting to PDF
        self.doc = Document('mytestdoc.doc', self.doc_simple1, self.workdir)
        pdf, cache_key = self.doc.convertToPDF()
        self.assertEqual(pdf[:6], '%PDF-1')
        self.assertEqual(cache_key, 'cc8c3b702ca3865608732f612691978b_1_1')

    def test_convert_to_pdf_w_cache_key(self):
        # Cached docs are retrieved
        self.doc = Document('mytestdoc.doc', self.doc_simple1, self.workdir)
        pdf1, cache_key1 = self.doc.convertToPDF()  # store doc in cache
        pdf2, cache_key2 = self.doc.convertToPDF(cache_key=cache_key1)
        assert pdf1 == pdf2
        assert cache_key1 == cache_key2
