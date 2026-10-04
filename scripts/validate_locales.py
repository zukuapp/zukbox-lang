#!/usr/bin/env python3
"""Validate ZUKBOX pair-array locale data without network or third-party modules."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

LOCALES = ('bulgaria', 'chinese', 'english', 'finland', 'french', 'germany',
           'hungary', 'indonesia', 'italiano', 'japanese', 'korean', 'latvia',
           'lithuania', 'netherlands', 'poland', 'romania', 'russia',
           'slovakia', 'spanish', 'turkey')
TOKEN = re.compile(r'%s[1-9]\d*')
ANY_TOKEN = re.compile(r'%s\d*')
SENTINEL = re.compile(r'placeholder', re.IGNORECASE)
KEY = re.compile(r'\{\{[^{}\r\n]+\}\}')
RUNTIME_PATH = 'src/js/language/application/LanguageUtil.ts'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(value):
    return dict(Counter(TOKEN.findall(value)))


def read_pairs(path):
    """Return all valid pairs and aggregate malformed rows instead of masking them."""
    errors = []
    try:
        rows = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [], [{'code': 'read', 'file': path.name, 'message': str(exc)}]
    if not isinstance(rows, list):
        return [], [{'code': 'pair_array', 'file': path.name}]
    pairs = []
    seen = set()
    for index, row in enumerate(rows, 1):
        context = {'file': path.name, 'row': index}
        if not isinstance(row, list) or len(row) != 2 or not all(isinstance(v, str) for v in row):
            errors.append({'code': 'pair_row', **context})
            continue
        key, value = row
        context['key'] = key
        if KEY.fullmatch(key) is None:
            errors.append({'code': 'key_wrapper', **context})
        if key in seen:
            errors.append({'code': 'duplicate', **context})
        seen.add(key)
        expected, actual = tokens(key), tokens(value)
        if expected != actual:
            errors.append({'code': 'placeholders', **context, 'expected': expected, 'actual': actual})
        if any(TOKEN.fullmatch(token) is None for token in ANY_TOKEN.findall(key + value)):
            errors.append({'code': 'invalid_placeholder', **context})
        # The runtime's String.replace replaces only the first occurrence per index.
        if any(count != 1 for count in expected.values()):
            errors.append({'code': 'repeated_source_placeholder', **context})
        indices = sorted(int(token[2:]) for token in expected)
        if indices and indices != list(range(1, max(indices) + 1)):
            errors.append({'code': 'source_placeholder_gap', **context})
        if SENTINEL.search(value):
            errors.append({'code': 'translation_sentinel', **context})
        pairs.append(row)
    return pairs, errors


def validate(directory):
    errors, tables = [], {}
    expected = {name + '.json' for name in LOCALES}
    actual = {path.name for path in directory.glob('*.json')}
    if actual != expected:
        errors.append({'code': 'locale_set', 'missing': sorted(expected - actual), 'extra': sorted(actual - expected)})
    for name in LOCALES:
        rows, issues = read_pairs(directory / (name + '.json'))
        tables[name] = rows
        errors.extend(issues)
    reference = {key for key, _ in tables['japanese']}
    for name, rows in tables.items():
        keys = {key for key, _ in rows}
        if keys != reference:
            errors.append({'code': 'key_set', 'locale': name, 'missing': sorted(reference - keys), 'extra': sorted(keys - reference)})
    return tables, errors


def file_manifest(directory):
    return {name + '.json': sha256(directory / (name + '.json')) for name in LOCALES}


def check_editor(directory, editor):
    errors = []
    target = editor / 'public/language'
    expected = {name + '.json' for name in LOCALES}
    actual = {p.name for p in target.glob('*.json')}
    if actual != expected:
        errors.append({'code': 'editor_locale_set', 'missing': sorted(expected - actual), 'extra': sorted(actual - expected)})
    for name in sorted(expected):
        path = target / name
        if not path.is_file() or path.read_bytes() != (directory / name).read_bytes():
            errors.append({'code': 'editor_sha', 'file': name})
    return errors


def source_audit(tables, editor):
    """Observe source references; dynamic keys cannot be proved stale by text search."""
    contents, files = [], {}
    paths = sorted((editor / 'src/js').rglob('*.ts'))
    paths = [p for p in paths if not p.name.endswith('.test.ts')]
    if (editor / 'index.html').is_file():
        paths.append(editor / 'index.html')
    for path in paths:
        contents.append(path.read_text(encoding='utf-8'))
        files[path.relative_to(editor).as_posix()] = sha256(path)
    # Join adjacent static TS strings, e.g. a multiline confirmation message.
    source = re.sub(r'"\s*\+\s*"', '', '\n'.join(contents))
    keys = {key for key, _ in tables['japanese']}
    observed = {key for key in keys if key in source or key[2:-2] in source}
    literal = {key for key in KEY.findall(source) if not any(c in key for c in ('$', '<', '>'))}
    return {
        'method': 'Static full keys or unwrapped Japanese text; adjacent double-quoted literals joined. Dynamic lookup and external templates prevent proving absence.',
        'source_files': files, 'observed_keys': sorted(observed),
        'unobserved_candidates': sorted(keys - observed),
        'literal_keys_missing_from_locales': sorted(literal - keys),
        'deletions': 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parents[1] / 'docs')
    parser.add_argument('--editor', type=Path, help='Check exact public/language bytes against this editor checkout')
    parser.add_argument('--sync-editor', action='store_true', help='Explicitly copy validated locale bytes to --editor')
    parser.add_argument('--manifest', type=Path, help='Check the recorded locale SHA256 manifest')
    parser.add_argument('--source-audit', action='store_true', help='Report static source observations; never delete candidates')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if (args.sync_editor or args.source_audit) and not args.editor:
        parser.error('--sync-editor/--source-audit requires --editor')
    tables, errors = validate(args.directory)
    manifest = file_manifest(args.directory) if not errors else {}
    pinned = None
    if args.manifest and not errors:
        try:
            pinned = json.loads(args.manifest.read_text(encoding='utf-8'))
            if manifest != pinned['files']:
                errors.append({'code': 'stale_manifest'})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({'code': 'manifest_read', 'message': str(exc)})
    if args.sync_editor and not errors:
        target = args.editor / 'public/language'
        target.mkdir(parents=True, exist_ok=True)
        actual = {p.name for p in target.glob('*.json')}
        extra = actual - set(manifest)
        if extra:
            errors.append({'code': 'editor_extra_files', 'extra': sorted(extra)})
        else:
            for name in manifest:
                temporary = target / (name + '.tmp')
                temporary.write_bytes((args.directory / name).read_bytes())
                temporary.replace(target / name)
    if args.editor and not errors:
        errors.extend(check_editor(args.directory, args.editor))
        if pinned and sha256(args.editor / RUNTIME_PATH) != pinned['consumer']['runtime_sha256']:
            errors.append({'code': 'runtime_sha', 'file': RUNTIME_PATH})
    report = {'locales': len(tables), 'unique_keys': len(dict(tables['japanese'])), 'files': manifest, 'errors': errors}
    if args.source_audit and not errors:
        report['source_audit'] = source_audit(tables, args.editor)
        for key in report['source_audit']['literal_keys_missing_from_locales']:
            errors.append({'code': 'editor_source_key_missing', 'key': key})
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'locales': report['locales'], 'unique_keys': report['unique_keys'], 'error_count': len(errors), 'errors': errors}, ensure_ascii=False))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
