# ZUKBOX 언어 리소스

이 저장소는 ZUKBOX 에디터의 다국어 UI 문자열을 관리하는 [Next2D 언어 저장소](https://github.com/Next2D/language.next2d.app)의 ZUKU 포크입니다. 원본 저작권과 [MIT 라이선스](LICENSE)를 유지합니다.

<a href="https://zukuapp.github.io/docs/"><img src="https://raw.githubusercontent.com/zukuapp/.github/main/profile/assets/developer-hero.png" alt="Trecillo × ZUKU 개발자 문서" width="760"></a>

**문서 입구:** [ZUKU 개발자 문서](https://zukuapp.github.io/docs/) · [ZUKBOX 에디터](https://github.com/zukuapp/zukbox)

## 파일 형식과 사용처

`docs/`의 로케일별 JSON은 `[원문 키, 번역문]` 문자열 쌍의 배열입니다. `docs/japanese.json`이 일본어 기준 파일이며, 다른 로케일도 같은 키를 사용하도록 관리합니다. 번역문 안의 `%s`, `%s1` 같은 자리표시는 문자열을 조합하는 코드가 사용하므로 보존해야 합니다.

에디터는 자기 저장소의 `public/language/*.json`을 `/language` 경로로 제공합니다. 이 저장소의 JSON을 수정해도 에디터의 배포 파일이 자동으로 갱신되지는 않습니다. 에디터와 언어 파일의 차이를 검토한 뒤 필요한 변경을 함께 반영합니다.

`docs/CNAME`은 원본 Next2D 언어 도메인을 가리킵니다. 이 저장소에는 npm 패키지 설정이나 ZUKU 배포 명령이 없습니다.

## 번역 수정

1. 새 문자열은 `docs/japanese.json`에 먼저 추가하고, 동일한 원문 키를 대상 로케일에도 넣습니다.
2. 번역문과 자리표시자를 검토합니다. 원문 키의 `{{...}}` 표기와 자리표시자는 임의로 바꾸지 않습니다.
3. 변경한 JSON을 확인하고 에디터의 `public/language/`와 동기화할 필요가 있는지 검토합니다.

다음 명령은 JSON 구문과 모든 항목의 기본 쌍 형식을 검사합니다.

현재 `docs/bulgaria.json`에는 일본어 기준 파일과 다른 원문 키가 한 항목 있으며,
`docs/japanese.json`에는 중복 원문 키도 있습니다. 아래 검사는 **키 일치나
자리표시자 보존까지 보장하지 않습니다.** 번역을 수정할 때는 변경한 키를
일본어 기준 파일 및 에디터 리소스와 직접 대조해 주세요.

```bash
python3 - <<'PY'
import json
from pathlib import Path

for path in sorted(Path('docs').glob('*.json')):
    rows = json.loads(path.read_text(encoding='utf-8'))
    assert isinstance(rows, list), path
    assert all(isinstance(row, list) and len(row) == 2 and
               all(isinstance(value, str) for value in row)
               for row in rows), path
    print(f'{path}: {len(rows)} entries')
PY
```

`translate_all.py`는 외부 `googletrans` 모듈과 번역 서비스에 의존하며, `docs/`의 여러 로케일을 직접 덮어씁니다. 의존성 버전이 저장소에 고정돼 있지 않으므로 일반적인 검증 명령으로 실행하지 않습니다. 대량 번역이 필요한 경우 변경 전후의 키와 자리표시자를 검토해 주세요.

기여 방법은 [조직 공통 가이드](https://github.com/zukuapp/.github/blob/main/CONTRIBUTING.md), 취약점 신고 방법은 [보안 정책](SECURITY.md)을 확인해 주세요.
