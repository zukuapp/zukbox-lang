export type LocaleCode = 'bg' | 'zh' | 'en' | 'fi' | 'fr' | 'de' | 'hu' | 'id'
  | 'it' | 'ja' | 'ko' | 'lv' | 'lt' | 'nl' | 'pl' | 'ro' | 'ru' | 'sk' | 'es' | 'tr';
export interface LocaleEntry {
  readonly filename: string;
  readonly sha256: string;
  readonly uniqueKeys: number;
}
export const localeManifest: Readonly<Record<LocaleCode, Readonly<LocaleEntry>>>;
export const localeCodes: readonly LocaleCode[];
export function localeURL(code: LocaleCode): URL;
export function loadLocale(code: LocaleCode, options?: {
  fetch?: (url: URL) => Promise<{ ok: boolean; arrayBuffer(): Promise<ArrayBuffer> }>;
}): Promise<[string, string][]>;
