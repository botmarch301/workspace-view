# Issue Tracking & Phase Gate Standard
> **ID**: CORE-ISS-001
> **Version**: 0.9.0
> **Status**: Draft
> **Last Updated**: 2026-03-28
> **Scope**: [Universal]

---

## 1. 이슈 레지스트리

### 1.1 위치

```
.spec-recipe/
  issues/
    registry.md     # 전체 이슈 목록 (자동 관리)
    archive/        # 해결된 이슈 아카이브
```

### 1.2 이슈 형식

```markdown
## ISS-NNN: [이슈 제목]
- **상태**: open | in-progress | resolved | wontfix | escalated
- **발견 시점**: [phase gate] (예: PG-1 요구사항→설계)
- **방향**: forward | backward | cross-cutting
- **발생 맥락**: [어떤 작업 중 발견되었는지]
- **영향 범위**: [영향받는 문서/코드 목록]
- **설명**: [구체적 문제 내용]
- **조치**: [해결 방법 또는 결정사항]
- **해결일**: [해결 시 기재]
```

### 1.3 이슈 상태 전이

```
open → in-progress → resolved → (archive/)
  │                      ↑
  └→ wontfix ─────────── │ (사유 필수)
  └→ escalated (ADR-0003 교정 상한 초과)
```

---

## 2. Phase Gate

### 2.1 Phase Gate 정의

| Gate | 전환 | 방향 | 확인 항목 |
|------|------|------|----------|
| PG-1 | 요구사항 → 설계 | forward | 요구사항 관련 open 이슈 0건, 모호한 요구사항 없음, glossary 완성 |
| PG-2 | 설계 → 구현 | forward | 설계 관련 open 이슈 0건, 추적성 매핑 완료, API/스키마 정의 완료 |
| PG-3 | 구현 → 테스트 | forward | 구현 관련 open 이슈 0건, 추적성 태그 부여 완료, 정적 분석 PASS |
| PG-4 | 테스트 → 완료 | forward | 전체 open 이슈 0건, 테스트 커버리지 충족, drift 0건, 활성 예외 리뷰 |
| PG-R1 | 코드 → 요구사항 | backward | 미문서화 기능(CODE-ONLY) 0건 또는 이슈로 등록 |
| PG-R2 | 테스트 → 설계 | backward | 테스트 실패의 원인 분류 완료 (설계 결함 vs 구현 버그) |

### 2.2 Phase Gate 검증

각 phase gate에서 `registry.md`를 파싱하여 해당 단계의 open 이슈가 0건인지 확인한다. 0건이 아니면 다음 단계 진행을 차단한다.

### 2.3 이슈 관리 규칙

- **중복 제거**: 동일 이슈가 다른 표현으로 등록되면 병합. 병합 시 원본 ID를 참조로 유지.
- **오기록 확인**: phase gate 통과 시 기존 이슈의 설명/영향 범위가 현재 상태와 일치하는지 확인.
- **누락 확인**: 검증 스크립트(verify-*.py)의 FAIL 항목이 이슈로 등록되어 있는지 확인. 미등록 FAIL은 자동 등록.
- **불필요 이슈 정리**: 해결된 이슈는 archive/로 이동. wontfix 이슈는 사유와 함께 archive.
