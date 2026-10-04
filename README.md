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

이 저장소는 ZUKBOX 에디터의 다국어 UI 문자열을 관리하는 [Next2D 언어 저장소](https://github.com/Next2D/language.next2d.app)의 ZUKU 포크입니다. 원본 저작권과 [MIT 라이선스](LICENSE)를 유지합니다.

**문서 입구:** [ZUKU 개발자 문서](https://zukuapp.github.io/docs/) · [ZUKBOX 에디터](https://github.com/zukuapp/zukbox)

## 파일 형식과 사용처

`docs/`의 로케일별 JSON은 `[원문 키, 번역문]` 문자열 쌍의 배열입니다. `docs/japanese.json`이 일본어 기준 파일이며, 다른 로케일도 같은 키를 사용하도록 관리합니다. 번역문 안의 `%s1`, `%s2` 같은 번호가 있는 자리표시는 문자열을 조합하는 코드가 사용하므로 보존해야 합니다.

에디터는 자기 저장소의 `public/language/*.json`을 `/language` 경로로 제공합니다. 이 저장소의 JSON을 수정해도 에디터의 배포 파일이 자동으로 갱신되지는 않습니다. 에디터와 언어 파일의 차이를 검토한 뒤 필요한 변경을 함께 반영합니다.

`docs/CNAME`은 원본 Next2D 언어 도메인을 가리킵니다. 이 저장소에는 npm 패키지 설정이나 ZUKU 배포 명령이 없습니다.

## 번역 수정

1. 새 문자열은 `docs/japanese.json`에 먼저 추가하고, 동일한 원문 키를 대상 로케일에도 넣습니다.
2. 번역문과 자리표시자를 검토합니다. 원문 키의 `{{...}}` 표기와 자리표시자는 임의로 바꾸지 않습니다.
3. 변경한 JSON을 확인하고 에디터의 `public/language/`와 동기화할 필요가 있는지 검토합니다.

다음 검사는 20개 로케일의 쌍 배열 형식, 중복 키, 일본어 기준과의 키 일치,
`%s1`부터 시작하는 자리표시자의 개수, 손상된 번역 토큰, 파일 해시를 확인합니다.
실제 편집기의 치환 함수는 같은 번호를 한 번만 치환하므로 각 자리표시자는
번역문에 정확히 한 번 있어야 합니다. 번호의 순서는 언어에 맞게 바꿀 수 있습니다.

```bash
python3 scripts/validate_locales.py --manifest validation/manifest.json
python3 -m unittest discover -s tests -v
```

에디터 체크아웃을 인접한 `../zukbox`에 준비한 후 다음 명령으로 20개 파일의
바이트 일치와 실제 소스의 UI 키를 확인합니다. 수정한 언어 파일을 명시적으로
복사하려면 첫 명령에 `--sync-editor`를 추가합니다. 잘못된 데이터는 복사하지 않습니다.

```bash
python3 scripts/validate_locales.py --editor ../zukbox --source-audit
ZUKBOX_EDITOR=../zukbox node --experimental-strip-types --test tests/runtime-interpolation.mjs
```

Node.js 24 이상은 실제 에디터의 `LanguageUtil.ts`를 직접 실행해 20개 언어의
모든 동적 문자열과 UI 키를 검사합니다. 전체 에디터 의존성 설치는 필요하지 않습니다.
`validation/repairs.json`에는 좁게 정정한 문구와 키의 변경 전후를 기록했습니다.
`validation/source-audit.json`의 32개 미관찰 키는 동적 사용 가능성이 있어 삭제하지
않았습니다. 정적 소스 검색은 실제 UI에 선언된 누락 키를 실패로 보고하지만,
키가 더 이상 쓰이지 않는다는 사실을 증명하지는 않습니다.

언어 저장소 CI는 `validation/manifest.json`에 기록한 편집기 커밋의 실제 함수를
검증합니다. 편집기 CI는 `.github/language-source.json`의 언어 커밋과 20개 파일
해시를 확인합니다. 파일을 변경하면 해시 기록과 편집기 리소스를 함께 갱신합니다.

### English validation guide

Locale files are arrays of `[source key, translation]` pairs. Run the Python checks
above before editing the consumer. Keep the same Japanese keys in all 20 locales,
with each numbered placeholder appearing exactly once. Reordering placeholders is
valid. The editor check verifies byte-for-byte synchronization and static UI keys;
the Node.js test executes the editor's real lookup and interpolation functions.
Use `--sync-editor` only for an explicit resource update. Unobserved dynamic keys
are reported for review and retained. Both CI workflows use recorded commit IDs
and SHA256 hashes; these checks do not deploy the editor or the language site.

`translate_all.py`는 외부 `googletrans` 모듈과 번역 서비스에 의존하며, `docs/`의 여러 로케일을 직접 덮어씁니다. 의존성 버전이 저장소에 고정돼 있지 않으므로 일반적인 검증 명령으로 실행하지 않습니다. 대량 번역이 필요한 경우 변경 전후의 키와 자리표시자를 검토해 주세요.

기여 방법은 [조직 공통 가이드](https://github.com/zukuapp/.github/blob/main/CONTRIBUTING.md), 취약점 신고 방법은 [보안 정책](SECURITY.md)을 확인해 주세요.
