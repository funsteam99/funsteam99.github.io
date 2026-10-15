"""Exercise the real publisher in an isolated checkout; no network or production writes."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('publisher', REPO/'scripts/prepare_scheduled_comic.py')
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)

class ScheduledComic(unittest.TestCase):
    def setUp(self):
        self.base = (REPO.parent/'tmp/scheduled-tests').resolve()
        self.base.mkdir(parents=True,exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.base)
        self.root = Path(self.temp.name)
        for folder in ['scripts','_data','_operations','modern-journey']:
            (self.root/folder).mkdir(parents=True)
        shutil.copyfile(REPO/'scripts/build_comic_panels.py', self.root/'scripts/build_comic_panels.py')
        shutil.copyfile(REPO/'_operations/scheduled-comic-panel-specs.json', self.root/'_operations/scheduled-comic-panel-specs.json')
        for file in ['comic_panel_specs.json','journey_episodes.json']:
            (self.root/'_data'/file).write_text('[]',encoding='utf-8')
        (self.root/'_data/comic_panels.json').write_text('{}',encoding='utf-8')
        (self.root/'modern-journey/index.html').write_text('    <article class="comic-feature" id="weekly-journey-ep01">existing</article>',encoding='utf-8')
        self.source = REPO/'assets/images/comics/weekly-journey-ep04.png'
        publisher.ROOT = self.root
    def tearDown(self):
        assert self.root.resolve().is_relative_to(self.base)
        self.temp.cleanup()
    def test_publish_retry_and_repair(self):
        publisher.prepare('04','悟空迷路九份！','2026-10-15',self.source)
        page = self.root/'modern-journey/index.html'
        first = page.read_bytes()
        publisher.prepare('04','悟空迷路九份！','2026-10-15',self.source)
        self.assertEqual(first,page.read_bytes())
        self.assertEqual(len(json.loads((self.root/'_data/journey_episodes.json').read_text(encoding='utf-8'))),1)
        data = json.loads((self.root/'_data/comic_panels.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['journey-04']['items']),13)
        self.assertNotIn('comic-page',page.read_text(encoding='utf-8'))
        page.write_text('    <article class="comic-feature" id="weekly-journey-ep04"><figure class="comic-page">old</figure></article>',encoding='utf-8')
        publisher.prepare('04','悟空迷路九份！','2026-10-15',self.source)
        self.assertIn("comic-reader.html id='journey-04'",page.read_text(encoding='utf-8'))
        self.assertNotIn('comic-page',page.read_text(encoding='utf-8'))
    def test_wrong_source_stops_before_changes(self):
        wrong = self.root/'wrong.png'
        wrong.write_bytes(b'wrong version')
        with self.assertRaisesRegex(AssertionError,'version differs'):
            publisher.prepare('04','test','2026-10-15',wrong)
        self.assertEqual((self.root/'_data/comic_panel_specs.json').read_text(), '[]')
        self.assertFalse((self.root/'assets').exists())
    def test_missing_spec_stops_before_changes(self):
        (self.root/'_operations/scheduled-comic-panel-specs.json').write_text('[]')
        with self.assertRaisesRegex(ValueError,'refusing whole-page fallback'):
            publisher.prepare('04','test','2026-10-15',self.source)
        self.assertFalse((self.root/'assets').exists())

if __name__ == '__main__':
    unittest.main()
