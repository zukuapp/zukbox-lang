import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('locales', ROOT / 'scripts/validate_locales.py')
locales = importlib.util.module_from_spec(spec)
spec.loader.exec_module(locales)


class LocaleValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / 'locale.json'

    def codes(self, rows):
        self.path.write_text(json.dumps(rows), encoding='utf-8')
        return {error['code'] for error in locales.read_pairs(self.path)[1]}

    def test_real_twenty_locales(self):
        tables, errors = locales.validate(ROOT / 'docs')
        self.assertEqual(errors, [])
        self.assertEqual({len(rows) for rows in tables.values()}, {390})

    def test_object_and_bad_pairs_are_rejected(self):
        self.assertIn('pair_array', self.codes({'{{a}}': 'a'}))
        self.assertIn('pair_row', self.codes([['{{a}}', 2], ['one'], 'text']))

    def test_duplicate_keys_are_rejected_even_when_identical(self):
        self.assertIn('duplicate', self.codes([['{{a}}', 'a'], ['{{a}}', 'a']]))

    def test_missing_closing_brace_is_rejected(self):
        self.assertIn('key_wrapper', self.codes([['{{a}', 'a']]))

    def test_reordered_tokens_are_valid(self):
        self.assertEqual(self.codes([['{{%s1 %s2}}', '%s2 / %s1']]), set())

    def test_missing_extra_repeated_and_unnumbered_tokens_are_rejected(self):
        for value in ('%s1', '%s1 %s2 %s3', '%s1 %s2 %s2', '%s %s2'):
            with self.subTest(value=value):
                self.assertIn('placeholders', self.codes([['{{%s1 %s2}}', value]]))
        self.assertIn('invalid_placeholder', self.codes([['{{a}}', '%s0']]))

    def test_translator_sentinels_are_rejected(self):
        self.assertIn('translation_sentinel', self.codes([['{{a}}', 'XPLACEholderx0X']]))

    def test_source_indices_must_be_contiguous_and_unique(self):
        self.assertIn('source_placeholder_gap', self.codes([['{{%s2}}', '%s2']]))
        self.assertIn('repeated_source_placeholder', self.codes([['{{%s1 %s1}}', '%s1 %s1']]))

    def test_missing_extra_keys_and_locales_are_rejected(self):
        directory = Path(self.temporary.name) / 'docs'
        shutil.copytree(ROOT / 'docs', directory)
        rows = json.loads((directory / 'english.json').read_text())
        rows[0][0] = '{{extra %s1 %s2 %s3 %s4 %s5}}'
        (directory / 'english.json').write_text(json.dumps(rows))
        (directory / 'turkey.json').unlink()
        errors = locales.validate(directory)[1]
        self.assertIn('locale_set', {e['code'] for e in errors})
        self.assertTrue(any(e['code'] == 'key_set' and e['locale'] == 'english' and e['missing'] and e['extra'] for e in errors))

    def test_editor_bytes_detect_translation_drift(self):
        editor = Path(self.temporary.name) / 'editor'
        shutil.copytree(ROOT / 'docs', editor / 'public/language')
        self.assertEqual(locales.check_editor(ROOT / 'docs', editor), [])
        (editor / 'public/language/english.json').write_text('[]')
        self.assertEqual(locales.check_editor(ROOT / 'docs', editor), [{'code': 'editor_sha', 'file': 'english.json'}])

    def test_dynamic_keys_are_observations_and_never_deleted(self):
        editor = Path(self.temporary.name) / 'editor'
        (editor / 'src/js').mkdir(parents=True)
        (editor / 'src/js/mock.ts').write_text('const a = "{{first" + " second}}"; const b = "history %s1";')
        tables = {'japanese': [['{{first second}}', 'a'], ['{{history %s1}}', '%s1'], ['{{dynamic}}', 'dynamic']]}
        audit = locales.source_audit(tables, editor)
        self.assertEqual(audit['observed_keys'], ['{{first second}}', '{{history %s1}}'])
        self.assertEqual(audit['unobserved_candidates'], ['{{dynamic}}'])
        self.assertEqual(audit['deletions'], 0)

    def test_stale_manifest_is_rejected_by_command(self):
        manifest = json.loads((ROOT / 'validation/manifest.json').read_text())
        manifest['files']['english.json'] = '0' * 64
        path = Path(self.temporary.name) / 'manifest.json'
        path.write_text(json.dumps(manifest))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_locales.py'), '--manifest', str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('stale_manifest', result.stdout)

    def test_invalid_data_is_never_synced_to_editor(self):
        directory = Path(self.temporary.name) / 'docs'
        shutil.copytree(ROOT / 'docs', directory)
        (directory / 'english.json').write_text('[]')
        editor = Path(self.temporary.name) / 'editor'
        shutil.copytree(ROOT / 'docs', editor / 'public/language')
        original = (editor / 'public/language/english.json').read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_locales.py'), '--directory', str(directory), '--editor', str(editor), '--sync-editor'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual((editor / 'public/language/english.json').read_bytes(), original)

    def test_missing_literal_editor_key_fails_source_check(self):
        editor = Path(self.temporary.name) / 'editor'
        shutil.copytree(ROOT / 'docs', editor / 'public/language')
        (editor / 'src/js').mkdir(parents=True)
        (editor / 'src/js/mock.ts').write_text('const text = "{{新しいUIキー}}";')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_locales.py'), '--editor', str(editor), '--source-audit'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('editor_source_key_missing', result.stdout)


if __name__ == '__main__':
    unittest.main()
