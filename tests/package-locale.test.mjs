import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { localeCodes, localeManifest, localeURL, loadLocale } from '../src/index.mjs';

const fileFetch = async url => new Response(await readFile(url));

test('every declared locale loads original bytes and all 390 unique pairs', async () => {
  assert.equal(localeCodes.length, 20);
  for (const code of localeCodes) {
    const bytes = await readFile(localeURL(code));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), localeManifest[code].sha256);
    assert.deepEqual(await loadLocale(code, { fetch: fileFetch }), JSON.parse(bytes));
  }
});

test('unknown, inherited, traversal and case-mismatched codes fail before fetching', async () => {
  let calls = 0;
  for (const code of ['unknown', '__proto__', 'constructor', '../english', 'EN', '', null, {}]) {
    assert.throws(() => localeURL(code), RangeError);
    await assert.rejects(loadLocale(code, { fetch: () => { calls++; } }), RangeError);
  }
  assert.equal(calls, 0);
});

test('locale lookup metadata is immutable', () => {
  assert.ok(Object.isFrozen(localeCodes));
  assert.ok(Object.isFrozen(localeManifest));
  for (const code of localeCodes) assert.ok(Object.isFrozen(localeManifest[code]));
  assert.equal(Reflect.set(localeManifest.en, 'filename', '../../outside.json'), false);
});

test('modified locale response fails the integrity check', async () => {
  const bytes = await readFile(localeURL('en'));
  await assert.rejects(loadLocale('en', { fetch: async () => new Response(Buffer.concat([bytes, Buffer.from(' ')])) }), /integrity mismatch/);
});

test('HTTP errors and incomplete fetch responses fail clearly', async () => {
  await assert.rejects(loadLocale('en', { fetch: async () => new Response('', { status: 404 }) }), /fetch failed/);
  await assert.rejects(loadLocale('en', { fetch: async () => ({ ok: true }) }), /fetch failed/);
  await assert.rejects(loadLocale('en', { fetch: null }), /fetch implementation/);
});
