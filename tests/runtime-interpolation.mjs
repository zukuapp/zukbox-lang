import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

const editor = resolve(process.env.ZUKBOX_EDITOR ?? '../zukbox');
const directory = resolve(process.env.ZUKBOX_LOCALES ?? 'docs');
const { $setMapping, $getMapping, $replace, $sprintf } = await import(
    pathToFileURL(resolve(editor, 'src/js/language/application/LanguageUtil.ts'))
);
const filenames = (await readdir(directory)).filter(name => name.endsWith('.json')).sort();
assert.equal(filenames.length, 20);

test('actual editor substitutes reordered indices and replaces once per index', () => {
    assert.equal($sprintf('%s2 / %s1', 'first', 'second'), 'second / first');
    assert.equal($sprintf('%s1 %s1', 'first'), 'first %s1');
    assert.equal($sprintf('no arguments'), '');
    $setMapping([]);
    assert.equal($replace('{{unknown}}'), '{{unknown}}');
});

for (const filename of filenames) {
    test(`${filename}: actual Map lookup and interpolation of every history template`, async () => {
        const rows = JSON.parse(await readFile(resolve(directory, filename), 'utf8'));
        $setMapping(rows);
        assert.equal($getMapping().size, rows.length, 'duplicate Map key would hide a row');
        assert.equal(rows.length, 390);
        for (const key of ['{{Photopea}}', '{{スタイル}}', '{{レイヤーの高さ}}', '{{作業履歴}}', '{{吸着}}']) {
            assert.notEqual($replace(key), key, `${filename}: missing actual UI lookup`);
        }
        for (const [key, translation] of rows) {
            assert.equal($replace(key), translation, key);
            const indices = [...key.matchAll(/%s([1-9]\d*)/g)].map(match => Number(match[1]));
            if (!indices.length) continue;
            const markers = Array.from({ length: Math.max(...indices) }, (_, i) => `TOKEN_${i + 1}_END`);
            const output = $sprintf($replace(key), ...markers);
            assert.doesNotMatch(output, /%s\d*|placeholder/i, key);
            for (const marker of markers) {
                assert.equal(output.split(marker).length - 1, 1, `${key}: ${marker}`);
            }
        }
    });
}
