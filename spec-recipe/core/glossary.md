# Spec-Recipe Glossary
> **ID**: CORE-GLO-001
> **Version**: 0.7.4
> **Status**: Draft
> **Last Updated**: 2026-03-19

Spec-Recipe 프레임워크 자체에서 사용하는 용어를 정의한다.

---

## 프레임워크 용어

| 용어 | 정의 |
|---|---|
| Spec-Recipe | 스펙 주도 개발의 도구 독립적 요구사항 표준 프레임워크 |
| Recipe | spec-recipe 프레임워크 자체. 코어 원칙, 검증 기준, 빌드 시스템, 스키마 등을 포함. "요리법을 만드는 작업" (Ref: ADR-0008) |
| Kitchen | Recipe에서 빌드된 산출물이 설치되어, 사용자가 실제로 SDD를 수행하는 환경. "요리법으로 실제 요리하는 현장" (Ref: ADR-0008) |
| Core | 도구에 의존하지 않는 원칙, 구조, 프로세스, 검증 기준의 집합 |
| Build Target | Core를 특정 도구의 형식으로 변환한 결과물 (예: BMAD 모듈, spec-kit 프리셋) |
| Tailoring Profile | 프로젝트 규모에 따른 적용 범위 조정 (Small / Medium / Large) |

## 적용 범위 분류

| 분류 | 의미 |
|---|---|
| Recipe-only | 프레임워크 개발에만 적용 (예: build.py 내부 구현) |
| Kitchen-only | 사용자 프로젝트에만 적용 (예: 기본 invariant 7개, pre-commit 동작) |
| Universal | Recipe와 Kitchen 양쪽에 적용 (예: 코어 원칙, ADR 프로세스) |

## 개발 프로세스 용어

| 용어 | 정의 |
|---|---|
| Spec-First | 코드 구현에 선행하여 스펙을 작성하는 원칙 |
| MAS | Machine-Actionable Specification. 기계가 읽고 검증할 수 있는 구조화된 스펙 |
| SoC | Separation of Concerns. What/Why/How의 역할 분리 |
| Traceability | 요구사항 → 코드 → 테스트 간 양방향 추적 가능성 |
| Forward Sync | 스펙에서 코드 스텁을 생성하는 방향 (Spec → Code) |
| Reverse Sync | 코드에서 스펙을 역추출하는 방향 (Code → Spec) |
| Drift | 스펙과 코드 간의 불일치 상태 |
| Drift Surface | 코드 변경 시 문서가 틀려질 수 있는 표면적 |
| 3-Way Alignment | Spec vs Code vs Test 3자 간 일치 여부 |
| Glossary-First | 프로젝트 용어를 먼저 정의하고 개발을 시작하는 원칙 |
| Enum-First | Enum/Constant를 스펙에서 선행 정의하는 원칙 |

## 검증 용어

| 용어 | 정의 |
|---|---|
| Deterministic Verification | AI 판단 없이 스크립트로 PASS/FAIL 판정 가능한 검증 |
| Semantic Verification | 사람 또는 분리된 AI 세션의 판단이 필요한 검증 |
| Verification Separation | 구현 주체와 검증 주체를 분리하는 원칙 |
| Session Start Check | 구현 세션 시작 시 코드-스펙 동기화 상태를 확인하는 절차 |
| Change Trigger | 특정 코드 변경 시 스펙 갱신을 요구하는 트리거 규칙 |

## 문서 용어

| 용어 | 정의 |
|---|---|
| Metadata Header | 문서 상단의 기계 파싱 가능한 메타 정보 (Title, ID, Status, Version) |
| Traceability Tag | 코드에 삽입하는 스펙 ID 참조 주석. 해당 언어의 주석 문법 + `Implements:` 또는 `Covers:` 키워드 |
| Traceability Matrix | 요구사항 ID → 구현 위치 → 테스트 위치의 매핑 테이블 |

## 테스트 용어

| 용어 | 정의 |
|---|---|
| TDD | Test-Driven Development. 테스트를 먼저 작성하고(Red), 통과하는 코드를 구현하고(Green), 리팩토링(Refactor)하는 사이클 |
| Requirement-Based Testing | 요구사항의 수용 시나리오에서 테스트 케이스를 도출하는 방법 |
| Requirement Coverage | 스펙 요구사항 대비 테스트 존재 비율 (FR이 `Covers:` 태그로 연결된 비율) |
| Code Coverage | 테스트 실행 시 코드가 실제로 실행되는 비율 (Line, Branch, Function) |
| Coverage Gap | 요구사항에 대응하는 테스트가 없는 상태 |
| Gap Analysis | 미커버 요구사항을 식별하고 보완 우선순위를 결정하는 절차 |
| Acceptance Test | 요구사항의 Given/When/Then 시나리오를 검증하는 테스트 |
| Ratchet | 코드 커버리지가 기존 비율 아래로 떨어지지 않도록 강제하는 정책 |

## 정적 분석 용어

| 용어 | 정의 |
|---|---|
| Cyclomatic Complexity | 함수 내 독립 실행 경로의 수. 높을수록 테스트와 이해가 어려움 |
| Cognitive Complexity | 코드를 인간이 이해하기 어려운 정도를 측정하는 지표 |
| Dead Code | 실행되지 않는 코드 (미사용 함수, 변수, import) |
| Code Duplication | 동일하거나 유사한 코드 블록이 여러 곳에 반복되는 상태 |
| SAST | Static Application Security Testing. 코드의 보안 취약점을 정적으로 분석 |
| Static Analysis Gate | 정적 분석 결과에 따라 빌드를 통과/차단하는 CI 단계 |

## 설치/운영 용어

| 용어 | 정의 |
|---|---|
| spec-recipe init | 프로젝트에 spec-recipe를 적용하는 초기화 명령. 설정 파일 생성, hook 설치, baseline 검증을 수행 |
| .spec-recipe.yml | 프로젝트 루트에 위치하는 설정 파일. 프로파일, 디렉토리 경로, hook 엄격도를 정의 |
| Baseline | 초기화 시점의 검증 결과. 이후 개선 추이를 측정하는 기준점 |
| Remediation Cycle | 검증 FAIL 발생 시 교정 계획 → 교정 실행 → 재검증을 반복하는 사이클 |
| Hook Strictness | pre-commit hook의 엄격도. small(경고만), medium(FAIL 시 차단), large(전 항목 차단) |

## Drift 분류 용어

| 용어 | 정의 |
|---|---|
| MATCH | 코드와 스펙의 대응 항목이 일치하는 상태 |
| DRIFT | 양쪽에 동일 항목이 존재하나 내용이 다른 상태 (예: enum 값 추가/삭제, 필드 타입 변경) |
| CODE-ONLY | 코드에만 존재하고 스펙에 대응 항목이 전혀 없는 상태 (미문서화 기능) |
| SPEC-ONLY | 스펙에만 존재하고 코드에 대응 항목이 전혀 없는 상태 (미구현 기능) |
