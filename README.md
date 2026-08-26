# zukbox-lang

ZUKBOX(애니메이션/저작 도구)용 **다국어 JSON** 리소스입니다.  
기본 언어는 일본어이며, 번역 스크립트로 다른 로케일을 생성·갱신합니다.

> GitHub: [zukuapp/zukbox-lang](https://github.com/zukuapp/zukbox-lang)  
> 업스트림: [Next2D/language.next2d.app](https://github.com/Next2D/language.next2d.app)  
> 소비처: [zukbox](https://github.com/zukuapp/zukbox)

## 구성

- 로케일별 JSON (에디터 UI 문자열)
- `translate_all.py` — 일괄 번역/동기화 보조
- `docs/` — 번역 가이드(있는 경우)

## 사용

에디터 저장소에서 이 패키지(또는 서브모듈/파일 참조)를 언어 소스로 읽습니다.  
문자열 키를 추가할 때는 기본(일본어) JSON을 먼저 갱신한 뒤 번역을 돌립니다.

```bash
python translate_all.py
```

## 관련

| 저장소 | 역할 |
|--------|------|
| [zukbox](https://github.com/zukuapp/zukbox) | 저작 도구 |
| [zukbox-player](https://github.com/zukuapp/zukbox-player) | 플레이어 |

## 라이선스

[MIT](LICENSE)

---

**ZUKBOX** · **ZUKU (즈쿠)** · Tresillo
