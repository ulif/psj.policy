# tests for cmd_oooconv module
import os
import unittest
from psj.policy.transforms.cmd_oooconv import Document
from Products.PortalTransforms.data import datastream


class DocumentTests(unittest.TestCase):

    def setUp(self):
        input_dir = os.path.join(os.path.dirname(__file__), 'input')
        self.doc_simple1_path = os.path.join(input_dir, 'simpledoc1.doc')
        self.doc_simple1 = open(self.doc_simple1_path, 'rb').read()
        self.idata = datastream('mytestdoc.doc')
        self.idata.setData(self.doc_simple1)
        self.doc = None   # to be set by tests

    def tearDown(self):
        pass

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
        html = self.doc.convert()
        assert 'A simple document.</p>' in html
