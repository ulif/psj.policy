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
        self.css_path = os.path.join(self.workdir, 'style.css')
        open(self.in_path, 'w').write('<html><body>Hi there!<body></html>')

    def tearDown(self):
        shutil.rmtree(self.workdir)

    @property
    def transform_options(self):
        # OPTIONS_HTML with 'psj_html' stripped from 'meta-procord'
        options = dict(OPTIONS_HTML)
        options['meta-procord'] = options['meta-procord'].replace(
            'psj_html', '')
        return options

    def create_source(self):
        # create an additional CSS file for use with the in_path HTML
        open(self.css_path, 'w').write('p: { \n  text-color: #f00; }')

    def test_registered(self):
        # make sure the processor is registered on startup
        assert 'psj_html' in get_entry_points('ulif.openoffice.processors')

    def test_args(self):
        # currently, we have no args to process
        proc = PSJHTMLProcessor()
        assert proc.args == []

    def test_process(self):
        # we can process docs. The result will be the input file, currently.
        proc = PSJHTMLProcessor()
        result_path, metadata = proc.process(
            self.in_path, {'error': False, 'error-descr': ''})
        assert result_path == self.in_path
        assert metadata == {'error': False, 'error-descr': ''}
