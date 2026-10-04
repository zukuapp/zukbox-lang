import { localeManifest } from './manifest.mjs';

export { localeManifest };
export const localeCodes = Object.freeze(Object.keys(localeManifest));

/** Resolve one exact locale code. No implicit language fallback or URL input. */
export function localeURL(code) {
  if (typeof code !== 'string' || !Object.hasOwn(localeManifest, code)) {
    throw new RangeError('Unknown ZUKU locale code');
  }
  return new URL(`../docs/${localeManifest[code].filename}`, import.meta.url);
}

/** Fetch exact validated pair-array bytes in browsers or through a supplied fetch. */
export async function loadLocale(code, { fetch: fetcher = globalThis.fetch } = {}) {
  const url = localeURL(code);
  if (typeof fetcher !== 'function') throw new TypeError('A fetch implementation is required');
  const response = await fetcher(url);
  if (!response || response.ok !== true || typeof response.arrayBuffer !== 'function') {
    throw new Error('Locale fetch failed');
  }
  const bytes = await response.arrayBuffer();
  if (!globalThis.crypto?.subtle) throw new Error('Web Crypto is required for locale integrity');
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  const hash = Array.from(new Uint8Array(digest), value => value.toString(16).padStart(2, '0')).join('');
  if (hash !== localeManifest[code].sha256) throw new Error('Locale integrity mismatch');
  const pairs = JSON.parse(new TextDecoder().decode(bytes));
  if (!Array.isArray(pairs) || pairs.length !== localeManifest[code].uniqueKeys
      || pairs.some(pair => !Array.isArray(pair) || pair.length !== 2
        || pair.some(value => typeof value !== 'string'))
      || new Set(pairs.map(pair => pair[0])).size !== pairs.length) {
    throw new Error('Invalid locale pair array');
  }
  return pairs;
}

