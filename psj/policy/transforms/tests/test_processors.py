# Tests for local ulif.openoffice processors.
import os
import shutil
import tempfile
import unittest
from ulif.openoffice.helpers import get_entry_points
from psj.policy.transforms.processors import PSJHTMLProcessor

class PSJHTMLProcessorTests(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.in_path = os.path.join(self.workdir, 'sample.html')
        open(self.in_path, 'w').write('<html><body>Hi there!<body></html>')

    def tearDown(self):
        shutil.rmtree(self.workdir)

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
