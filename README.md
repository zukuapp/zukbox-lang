<!-- BEGIN ZUKU OFFICIAL BRAND -->
<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <a href="https://docs.zuzunza.com/">
    <picture>
      <source media="(prefers-color-scheme: dark)"
        srcset=".github/branding/zuku-logo-dark.png">
      <img src=".github/branding/zuku-logo-light.png"
        alt="ZUKU" width="320">
    </picture>
  </a>
</p>
<p align="center">ZUKU - 내가 불러 일으키는 새로운 창작.</p>
<!-- markdownlint-enable MD033 MD041 -->
<!-- END ZUKU OFFICIAL BRAND -->

# ZUKBOX 언어 리소스

![version](https://img.shields.io/badge/version-v27.26102701-informational)

이 저장소는 ZUKBOX 에디터의 다국어 UI 문자열을 관리합니다. [Next2D 언어 저장소](https://github.com/Next2D/language.next2d.app)의 ZUKU 포크이며, 원본 저작권과 [MIT 라이선스](LICENSE)를 유지합니다.

관련 문서: [ZUKU 개발자 문서](https://zukuapp.github.io/docs/) · [ZUKBOX 에디터](https://github.com/zukuapp/zukbox)

## 개요

- `docs/`의 로케일별 JSON은 `[원문 키, 번역문]` 문자열 쌍의 배열입니다.
- `docs/japanese.json`이 일본어 기준 파일입니다. 다른 19개 로케일도 같은 키를 사용합니다.
- 번역문의 `%s1`, `%s2` 같은 번호 자리표시자는 문자열을 조합하는 코드가 사용합니다. 자리표시자는 보존합니다.
- 에디터는 자기 저장소의 `public/language/*.json`을 `/language` 경로로 제공합니다. 이 저장소의 JSON을 수정해도 에디터의 배포 파일은 자동으로 갱신되지 않습니다.
- `docs/CNAME`은 원본 Next2D 언어 도메인을 가리킵니다. npm 배포 파일에는 포함하지 않습니다.

## 요구 사항

| 용도 | 요구 사항 |
| --- | --- |
| 로케일 검사 | Python 3.12 (CI 기준) |
| 패키지 검사, 런타임 보간 테스트 | Node.js 24 이상 |
| 브라우저에서 `loadLocale` 사용 | HTTPS 또는 localhost의 Web Crypto 환경 |
| 에디터 호환성 검사 | 인접 경로의 ZUKBOX 에디터 체크아웃 (예: `../zukbox`) |

## 설치

`@zuku/lang@0.1.0`은 기존 20개 JSON의 바이트와 MIT 저작권 고지를 유지하는 리소스 패키지입니다. 공개된 릴리스는 다음 명령으로 설치합니다.

```bash
npm install @zuku/lang@0.1.0
```

## 사용법

### JavaScript API

| API | 동작 |
| --- | --- |
| `localeCodes` | 지원하는 언어 코드 배열을 제공합니다. |
| `localeURL(code)` | 정확한 언어 코드에 해당하는 파일 URL을 반환합니다. |
| `loadLocale(code, options)` | 파일 해시를 확인한 뒤 문자열 쌍 배열을 반환합니다. `options.fetch`로 fetch 구현을 지정합니다. |

미지원 코드는 요청 전에 `RangeError`로 실패합니다. 다른 언어로 자동 대체하지 않습니다.

```js
import { localeCodes, localeURL, loadLocale } from '@zuku/lang';
const koURL = localeURL('ko');
const pairs = await loadLocale('ko'); // HTTPS 또는 localhost의 Web Crypto 환경
const mapping = new Map(pairs);
```

JSON 파일은 `@zuku/lang/locales/ko.json` 같은 하위 경로로 직접 가져옵니다. 지원 언어 코드는 다음과 같습니다.

```text
bg zh en fi fr de hu id it ja ko lv lt nl pl ro ru sk es tr
```

Node.js에서는 `readFile(localeURL('ko'))`로 원본 파일을 읽거나, JSON 모듈을 `with { type: 'json' }`으로 가져옵니다. Node.js의 기본 fetch는 file URL을 읽지 않습니다. Node.js에서 `loadLocale`을 사용하려면 파일을 읽는 fetch 구현을 `options.fetch`로 전달합니다.

### 번역 수정

1. 새 문자열을 `docs/japanese.json`에 먼저 추가합니다.
2. 같은 원문 키를 대상 로케일에 추가합니다.
3. 번역문과 자리표시자를 검토합니다. 원문 키의 `{{...}}` 표기와 자리표시자는 바꾸지 않습니다.
4. 아래 검사를 실행합니다.
5. 에디터의 `public/language/`와 동기화가 필요한지 검토합니다.

각 번호 자리표시자는 번역문에 정확히 한 번 있어야 합니다. 에디터의 치환 함수는 같은 번호를 한 번만 치환합니다. 번호의 순서는 언어에 맞게 바꿔도 됩니다.

### 로케일 검사

다음 검사는 20개 로케일에 대해 쌍 배열 형식, 중복 키, 일본어 기준과의 키 일치, `%s1`부터 시작하는 자리표시자 개수, 손상된 번역 토큰, 파일 해시를 확인합니다.

```bash
python3 scripts/validate_locales.py --manifest validation/manifest.json
python3 -m unittest discover -s tests -v
```

패키지 매니페스트와 로더는 다음 명령으로 검사합니다. 이 명령은 파일을 번역하거나 배포하지 않습니다.

```bash
npm run generate:check
npm run test:package
```

### 에디터 호환성 검사

에디터 체크아웃을 `../zukbox`에 준비한 뒤 다음 명령을 실행합니다. 첫 명령은 20개 파일의 바이트 일치와 에디터 소스의 UI 키를 확인합니다. 두 번째 명령은 에디터의 `LanguageUtil.ts`를 직접 실행해 20개 언어의 동적 문자열과 UI 키를 검사합니다. 전체 에디터 의존성은 설치하지 않습니다.

```bash
python3 scripts/validate_locales.py --editor ../zukbox --source-audit
ZUKBOX_EDITOR=../zukbox node --experimental-strip-types --test tests/runtime-interpolation.mjs
```

`--source-audit`는 에디터 소스에 선언됐지만 로케일에 없는 키를 오류로 보고합니다. `--sync-editor`는 에디터 리소스를 명시적으로 갱신할 때만 사용합니다.

## 설정

### `scripts/validate_locales.py` 옵션

| 옵션 | 설명 |
| --- | --- |
| `--directory` | 로케일 JSON 디렉터리입니다. 기본값은 `docs/`입니다. |
| `--manifest` | 기록된 로케일 SHA256 매니페스트와 비교합니다. |
| `--editor` | 지정한 에디터 체크아웃의 `public/language` 바이트와 비교합니다. |
| `--sync-editor` | 검증된 로케일 바이트를 `--editor` 경로로 복사합니다. 잘못된 데이터는 복사하지 않습니다. `--editor`가 필요합니다. |
| `--source-audit` | 정적 소스 검색 결과를 보고합니다. 후보 키를 삭제하지 않습니다. `--editor`가 필요합니다. |
| `--report` | 결과 보고서를 저장할 경로입니다. |

### 환경 변수

| 변수 | 설명 |
| --- | --- |
| `ZUKBOX_EDITOR` | `tests/runtime-interpolation.mjs`가 사용하는 에디터 체크아웃 경로입니다. |

### 검증 기록 파일

| 파일 | 내용 |
| --- | --- |
| `validation/manifest.json` | 20개 로케일 파일의 SHA256 해시와 검증 대상 에디터 커밋 |
| `validation/repairs.json` | 정정한 문구와 키의 변경 전후 |
| `validation/source-audit.json` | 정적 소스 검색에서 관찰되지 않은 32개 키 |

언어 저장소 CI는 `validation/manifest.json`에 기록한 에디터 커밋의 함수를 검증합니다. 에디터 CI는 `.github/language-source.json`의 언어 커밋과 20개 파일 해시를 확인합니다. 로케일 파일을 변경하면 해시 기록과 에디터 리소스를 함께 갱신합니다.

## 문제 해결

| 증상 | 원인과 조치 |
| --- | --- |
| `Unknown ZUKU locale code` | 지원 언어 코드 목록에 없는 코드입니다. 정확한 코드를 사용합니다. |
| `A fetch implementation is required` | 실행 환경에 fetch가 없습니다. `options.fetch`로 구현을 전달합니다. |
| `Web Crypto is required for locale integrity` | Web Crypto가 없는 환경입니다. HTTPS 또는 localhost에서 실행합니다. |
| `Locale integrity mismatch` | `loadLocale`이 받은 바이트의 SHA-256이 `src/manifest.mjs`의 기록과 다릅니다. 패키지의 로케일 파일을 변환 없이 그대로 제공합니다. `src/manifest.mjs`는 `npm run generate`가 `validation/manifest.json`에서 생성하며, `npm run generate:check`는 생성 파일이 오래되면 실패합니다. |
| 소스 검사가 미관찰 키를 보고함 | 정적 검색은 동적으로 조합되는 키를 찾지 못합니다. 미관찰 키는 검토 대상으로 보고하고 삭제하지 않습니다. |

`translate_all.py`는 외부 `googletrans` 모듈과 번역 서비스를 사용하며 `docs/`의 여러 로케일을 직접 덮어씁니다. 의존성 버전이 저장소에 고정돼 있지 않으므로 검증 명령에 포함하지 않습니다. 대량 번역 후에는 변경 전후의 키와 자리표시자를 검토합니다.

## 변경 이력

[CHANGELOG.md](CHANGELOG.md)에 기록합니다.

## English summary

Locale files are arrays of `[source key, translation]` pairs. Keep the same Japanese keys in all 20 locales. Each numbered placeholder appears exactly once in a translation; reordering placeholders is valid.

| Task | Command |
| --- | --- |
| Validate locales | `python3 scripts/validate_locales.py --manifest validation/manifest.json` |
| Run regressions | `python3 -m unittest discover -s tests -v` |
| Check package manifest and loader | `npm run generate:check && npm run test:package` |

`localeURL` resolves exact locale codes. JSON subpaths such as `@zuku/lang/locales/ko.json` are exported. `loadLocale` requires Web Crypto in an HTTPS or localhost browser, or a supplied `fetch` in Node.js. Unknown codes fail before a request. No implicit fallback is applied.

Run the Python checks before updating the editor. The editor check verifies byte-for-byte synchronization and static UI keys. The Node.js test executes the editor's lookup and interpolation functions. `--sync-editor` copies files only when passed explicitly. Unobserved dynamic keys are reported and retained. Both CI workflows use recorded commit IDs and SHA256 hashes. These checks do not deploy the editor or the language site.

## 기여와 보안

- 기여 방법: [조직 공통 가이드](https://github.com/zukuapp/.github/blob/main/CONTRIBUTING.md)
- 취약점 신고: [보안 정책](SECURITY.md)
