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
        self.css_sample_path = os.path.join(input_dir, 'sample.css')
        self.css_sample = open(self.css_sample_path, 'r').read()
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
        # create a sample css
        open(os.path.join(self.workdir, 'sample.css'), 'w').write(
            self.css_sample)
        result_path, metadata = proc.process(
            self.in_path, {'error': False, 'error-descr': ''})
        assert metadata == {'error': False, 'error-descr': ''}

    def test_get_css(self):
        # we can get css files placed in result.
        for name in ['foo.html', 'foo.css', 'bar.css', 'baz.css']:
            open(os.path.join(self.workdir, name), 'w').write('foo')
        proc = PSJHTMLProcessor()
        result = list(proc.get_css(self.workdir))
        self.assertEqual(
            result, [
                os.path.join(self.workdir, 'bar.css'),
                os.path.join(self.workdir, 'baz.css'),
                os.path.join(self.workdir, 'foo.css'),
                ])

    def test_fix_css(self):
        # we can 'fix' code in CSS
        code = self.css_sample
        proc = PSJHTMLProcessor()
        self.assertEqual(  # empty CSS
            proc.fix_css(''), '')
        self.assertEqual(  # base CSS
            proc.fix_css('p {color:#000;}'),
            '#psj-doc p{color:#000}')
        self.assertEqual(  # CSS with OR selector (,)
            proc.fix_css('div, p {color:#000;}'),
            '#psj-doc div,#psj-doc p{color:#000}')
        self.assertEqual(  # CSS with linebreaks
            proc.fix_css('p {color:#000;}\ndiv#num1 {color: #fff}'),
            '#psj-doc p{color:#000}#psj-doc div#num1{color:#fff}')
        self.assertEqual(  # 'body' selector replaced
            proc.fix_css('body {color:#000;}'),
            '#psj-doc{color:#000}')
