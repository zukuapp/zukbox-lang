import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const mapping = {
  bg: 'bulgaria.json', zh: 'chinese.json', en: 'english.json', fi: 'finland.json',
  fr: 'french.json', de: 'germany.json', hu: 'hungary.json', id: 'indonesia.json',
  it: 'italiano.json', ja: 'japanese.json', ko: 'korean.json', lv: 'latvia.json',
  lt: 'lithuania.json', nl: 'netherlands.json', pl: 'poland.json', ro: 'romania.json',
  ru: 'russia.json', sk: 'slovakia.json', es: 'spanish.json', tr: 'turkey.json',
};
const source = JSON.parse(await readFile(new URL('validation/manifest.json', root), 'utf8'));
if (JSON.stringify(Object.values(mapping).sort()) !== JSON.stringify(Object.keys(source.files).sort())) {
  throw new Error('Package locale mapping does not cover the exact validated file set');
}
const entries = Object.entries(mapping).map(([code, filename]) => [code, {
  filename, sha256: source.files[filename], uniqueKeys: source.unique_keys,
}]);
const body = `// Generated from validation/manifest.json; run npm run generate:check.\n`
  + `export const localeManifest = Object.freeze(Object.fromEntries(\n`
  + `${JSON.stringify(entries, null, 2)}.map(([code, entry]) => [code, Object.freeze(entry)])\n));\n`;
const target = new URL('src/manifest.mjs', root);
if (process.argv.includes('--check')) {
  if (await readFile(target, 'utf8') !== body) throw new Error('Package locale manifest is stale');
} else {
  await mkdir(fileURLToPath(new URL('src/', root)), { recursive: true });
  await writeFile(target, body);
}

