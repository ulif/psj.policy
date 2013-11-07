# Tests for local ulif.openoffice processors.
import os
import shutil
import tempfile
import unittest
from ulif.openoffice.client import Client
from ulif.openoffice.helpers import get_entry_points
from psj.policy.transforms.cmd_oooconv import OPTIONS_HTML
from psj.policy.transforms.processors import PSJHTMLProcessor


class PSJHTMLProcessorTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.in_path = os.path.join(self.workdir, 'sample.html')
        self.doc_path = os.path.join(self.workdir, 'sample.doc')
        input_dir = os.path.join(os.path.dirname(__file__), 'input')
        self.doc_simple1_path = os.path.join(input_dir, 'simpledoc1.doc')
        shutil.copy(self.doc_simple1_path, self.doc_path)
        self.result_path = None

    def tearDown(self):
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
        if self.result_path:
            shutil.rmtree(os.path.dirname(self.result_path))

    @property
    def transform_options(self):
        # OPTIONS_HTML with 'psj_html' stripped from 'meta-procord'
        options = dict(OPTIONS_HTML)
        options['meta-procord'] = options['meta-procord'].replace(
            'psj_html', '')
        return options

    def create_source(self):
        # create an additional CSS file for use with the in_path HTML
        client = Client()
        self.result_path, cache_key, metadata = client.convert(
            self.doc_path, self.transform_options)
        assert self.result_path is not None
        #self.assertEqual(os.listdir(os.path.dirname(self.result_path)), 'asd')

    def test_registered(self):
        # make sure the processor is registered on startup
        assert 'psj_html' in get_entry_points('ulif.openoffice.processors')

    def test_args(self):
        # currently, we have no args to process
        proc = PSJHTMLProcessor()
        assert proc.args == []

    def test_process(self):
        # we can process docs. The result will be the input file, currently.
        self.create_source()
        proc = PSJHTMLProcessor()
        result_path, metadata = proc.process(
            self.in_path, {'error': False, 'error-descr': ''})
        assert metadata == {'error': False, 'error-descr': ''}
