# ADR-0003: Invariant 규칙의 사용자 비활성화 정책

> **ID**: ADR-0003
> **Status**: Proposed
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: v0.9.0 제약 체계 (constraints/invariants/)

## 1. 맥락 및 문제 정의

Invariant는 "절대 위반 불가"로 설계된 최상위 제약이다. 기본 제공되는 7개 보안 규칙(하드코딩 시크릿, SQL 인젝션, eval/exec 등)이 여기에 해당한다.

그러나 현실에서는 예외가 필요한 경우가 있다:
- 테스트 코드에서 의도적으로 취약 패턴을 작성하는 경우
- 레거시 코드의 점진적 마이그레이션 중
- 특정 도메인에서 보안 규칙이 과도한 경우 (예: 로컬 전용 스크립트)

완전히 비활성화를 금지하면 false positive에 의한 개발 차단이 발생하고, 자유롭게 비활성화를 허용하면 invariant 체계의 의미가 사라진다.

## 2. 고려된 대안

### 2.1 대안 1: 완전 금지
- **Pros**: invariant의 절대성 보장
- **Cons**: false positive 시 탈출구 없음, 실무 적용 시 불만 누적 → 프레임워크 자체를 회피

### 2.2 대안 2: 자유 비활성화
- **Pros**: 유연
- **Cons**: invariant와 principle의 차이 소멸, 보안 규칙 무력화

### 2.3 대안 3: 명시적 사유 기재 시 허용 (explicit-only)
- **Pros**: 비활성화 가능하되, 사유가 기록으로 남아 감사 가능
- **Cons**: 사유를 형식적으로 작성하면 실효 없음 → 추가 강제 필요

## 3. 결정

**대안 3: 명시적 사유 기재 + 범위 제한(explicit-only)**을 선택한다.

### 3.1 결정의 근거

1. 비활성화가 아닌 **예외(exception)** 개념으로 접근한다. 규칙 자체를 끄는 게 아니라, 특정 파일/라인에 대한 예외를 선언한다.
2. 예외 선언에는 반드시 사유, 범위(파일/라인), 만료일을 포함해야 한다.
3. 예외는 이슈 레지스트리(ADR-0001)에 자동 등록되어, phase gate에서 검토 대상이 된다.
4. 만료일이 지난 예외는 자동으로 HALT로 복원된다.

### 3.2 예외 선언 형식

```yaml
# .spec-recipe/constraints/exceptions/exception-001.yml
id: EXC-001
target_constraint: INV-SEC-001
scope:
  files: ["tests/security/test_injection.py"]
  lines: [42, 43, 44]          # 선택적
reason: "SQL 인젝션 탐지 테스트를 위한 의도적 취약 패턴"
expires: 2026-06-30              # 필수. 영구 예외는 허용하지 않음.
approved_by: "Mingi"
created: 2026-03-28
registered_issue: ISS-XXX        # 이슈 레지스트리에 자동 등록
```

### 3.3 강제 규칙

- 예외 파일 없이 invariant 검증을 건너뛰는 것은 불가
- 예외의 `expires`는 최대 90일 (설정으로 조정 가능)
- 만료된 예외가 있는 상태에서 커밋 시 HALT
- phase gate PG-4(완료)에서 활성 예외 목록 리뷰 필수

## 4. 영향

- **Positive**: false positive 대응 가능, 감사 추적 가능, 임시적 예외만 허용
- **Negative**: 예외 관리 오버헤드
- **Follow-up**: 
  - constraints/exceptions/ 디렉토리 추가
  - 예외 만료 검사를 pre-commit에 추가
  - 이슈 레지스트리와 연동
