# Constraint YAML Schema
> **ID**: CORE-CST-001
> **Version**: 0.9.0
> **Status**: Draft
> **Last Updated**: 2026-03-28
> **Scope**: [Universal] — Recipe에서 정의, Kitchen에서 사용

---

## 1. 디렉토리 구조

```
.spec-recipe/
  constraints/
    invariants/           # 보안 등 절대 규칙 (코어 제공 + 사용자 추가)
    principles/           # 코어 원칙 (코어에서 자동 생성)
    conventions/          # 프로젝트별 컨벤션 (사용자 정의)
    exceptions/           # 예외 선언 (ADR-0003)
    index.yml             # 전체 제약 인덱스 (자동 생성)
```

## 2. 제약 계층

| 계층 | 위반 대응 | 관리 주체 | 유예 |
|------|----------|----------|------|
| Invariant | HALT (전체 커밋 차단) | 코어 제공 + 사용자 추가 | 예외 선언만 가능 (ADR-0003) |
| Principle | BLOCK (해당 파일 커밋 차단) | 코어에서 자동 생성 | Phase gate 이슈 등록 후 유예 |
| Convention | BLOCK (해당 파일 커밋 차단) | 사용자 정의 | Phase gate 이슈 등록 후 유예 |

WARN은 사용하지 않는다. 정의된 모든 규칙은 강제된다. (Ref: ADR-0002)

## 3. Constraint YAML 스키마

```yaml
# 필수 필드
id: string              # 고유 ID (예: INV-SEC-001, PRC-TRC-001, CONV-STYLE-001)
layer: enum             # invariant | principle | convention
name: string            # 규칙 이름
severity: enum          # halt | block

# 적용 범위
scope:
  files: string | list  # glob 패턴 (예: "**/*.py", ["src/**", "lib/**"])
  exclude: list         # 제외 패턴 (선택)

# 검증 방법 (depth별)
detection:
  fast:                 # 파일 저장 시 (선택)
    method: enum        # regex | ast | script | tool
    patterns: list      # method=regex인 경우
    rules: list         # method=ast인 경우
    command: string     # method=script인 경우
  normal:               # 커밋 시 (필수)
    method: enum
    patterns: list
    rules: list
    command: string
  deep:                 # CI 시 (선택)
    method: enum
    tool: string        # method=tool인 경우 (외부 도구명)
    config: string      # 도구 설정 파일 경로

# 교정 안내
remediation: string     # 위반 시 교정 방법 (마크다운)

# 메타데이터
tags: list              # 분류 태그 (선택, 예: [security, authentication])
ref: string             # 참조 (선택, 예: ADR-0003, OWASP-A1)
```

## 4. 예외 YAML 스키마 (ADR-0003)

```yaml
# 필수 필드
id: string              # 고유 ID (예: EXC-001)
target_constraint: string  # 대상 constraint ID
scope:
  files: list           # 대상 파일 (구체적 경로, 와일드카드 금지)
  lines: list           # 대상 라인 (필수, 파일 전체 예외 불가)
reason: string          # 예외 사유 (구체적)
expires: date           # 만료일 (필수, 최대 90일)
approved_by: string     # 승인자
created: date           # 생성일
related_adr: string     # 관련 ADR 또는 이슈 ID (선택)
```

## 5. index.yml 스키마 (자동 생성)

```yaml
# spec-recipe가 자동 생성. 수동 수정 금지.
generated_at: datetime
constraint_hash: string     # 전체 constraint 디렉토리의 해시

invariants:
  - id: INV-SEC-001
    name: "하드코딩된 시크릿 금지"
    severity: halt
    file: "invariants/no-hardcoded-secrets.yml"

principles:
  - id: PRC-TRC-001
    name: "추적성 태그 필수"
    severity: block
    file: "principles/traceability.yml"

conventions: []             # 사용자 정의 시 채워짐

exceptions:
  - id: EXC-001
    target: INV-SEC-001
    expires: 2026-06-30
    file: "exceptions/exc-001.yml"

stats:
  total: 14
  invariants: 7
  principles: 7
  conventions: 0
  exceptions: 0
  active_exceptions: 0
  expired_exceptions: 0
```
