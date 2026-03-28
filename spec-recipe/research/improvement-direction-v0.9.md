# spec-recipe v0.9.0 개선 방향

> 작성일: 2026-03-28
> 근거: 리서치 보고서 + 설계안 + 제3자 검토서 + 블로그 2편 분석
> 상태: 검토 대기

---

## 1. 목표

### 1.1 포지셔닝

"원칙 선언 → agent 주입 → 기계적 강제 → 위반 피드백 → 측정 → 개선"의 **전 구간 파이프라인**을 agent 독립적으로 제공하는 메타 프레임워크.

현존 도구들은 이 파이프라인의 일부만 커버한다:

| 구간 | 담당 도구 | spec-recipe 현재 |
|------|----------|-----------------|
| 원칙 선언 | Spec Kit, BMAD, OpenSpec | O (principles.md) |
| agent 주입 | Agent OS, Kiro Steering | **X** |
| 기계적 강제 | Entrix, pre-commit | 부분 (pre-commit) |
| 위반 피드백 | Kiro Hooks | **X** |
| 측정 | Scorecard | **X** |
| 개선 | (해당 도구 없음) | **X** |

### 1.2 목표 성숙도

| 지표 | v0.8.0 (현재) | v0.9.0 (목표) |
|------|-------------|-------------|
| CMMI 수준 | Level 3 (Defined) | Level 4~5 (Quantitatively Managed ~ Optimizing) |
| ISO 12207 커버리지 | 4/7 프로세스 | 6/7 프로세스 |
| 하네스 레이어 | L1(스펙) + L3(검증) | L1 + L2 + L3 + L4 + L5 |

---

## 2. 개선 영역

### 2.1 제약 체계 (Constraint System)

**현재 문제**: principles.md에 7개 원칙이 정의되어 있지만, (1) agent가 이를 읽지 않고, (2) 보안 규칙과 네이밍 컨벤션이 같은 레벨에 혼재하며, (3) 위반 시 대응이 pre-commit 차단 하나뿐이다.

**개선 방향**:

**(a) 3계층 제약 모델**

```
Invariant (불변)  →  위반 시 HALT   →  유예 불가
Principle (원칙)  →  위반 시 BLOCK  →  Milestone 유예 가능
Convention (컨벤션) → 위반 시 WARN  →  자유, 반복 시 승격
```

- 각 제약은 YAML 파일로 정의 (id, layer, severity, detection, remediation)
- `.spec-recipe/constraints/` 디렉토리에 계층별 저장
- 기본 invariant 7개(보안) + principles 7개(코어에서 자동 변환) 제공
- convention은 사용자가 추가 확장

**(b) 검증 깊이 (depth) 도입** -- 검토서 R1

Entrix의 tier별 검증을 차용. 동일 제약에 대해 상황별 검증 깊이를 다르게 적용한다.

| 시점 | depth | 방법 | 용도 |
|------|-------|------|------|
| 파일 저장 시 | fast | regex 패턴 매칭 | 즉각적 경고 |
| 커밋 시 | normal | AST 분석 + regex | 커밋 게이트 |
| CI/Push 시 | deep | 외부 도구(bandit, semgrep 등) 연동 | 최종 검증 |

```yaml
# 제약 정의 예시
id: INV-SEC-001
layer: invariant
name: "하드코딩된 시크릿 금지"
detection:
  fast:    # 파일 저장 시
    method: regex
    patterns: ['password\s*=\s*["\'][^"\']{8,}']
  normal:  # 커밋 시
    method: ast
    rules: ["string_literal_in_assignment_to_secret_name"]
  deep:    # CI 시
    method: tool
    tool: "detect-secrets"
    config: ".detect-secrets.baseline"
```

**(c) convention 자동 추출** -- 검토서 R6

Agent OS의 `/discover-standards` 패턴을 차용.

```
spec-recipe discover-conventions
  → 기존 코드 분석 (네이밍 패턴, import 구조, 디렉토리 규칙)
  → convention YAML 초안 자동 생성
  → 사용자 검토/수정 후 확정
```

### 2.2 Agent 주입 파이프라인 (Agent Injection)

**현재 문제**: 제약이 정의되어도 agent가 이를 인지하지 못한다.

**개선 방향**:

**(a) constraint → agent 규칙 파일 자동 변환**

build.py를 확장하여 동일한 코어 제약에서 agent별 규칙 파일을 생성한다.

| 소스 | → Codex | → Cursor | → Kiro | → Claude Code |
|------|---------|----------|--------|--------------|
| invariants/ | AGENTS.md ## Absolute Rules | .cursor/rules/security.md | .kiro/steering/security.md | CLAUDE.md ## Security |
| principles/ | AGENTS.md ## Principles | .cursor/rules/principles.md | .kiro/steering/standards.md | CLAUDE.md ## Principles |
| conventions/ | AGENTS.md ## Conventions | .cursor/rules/style.md | .kiro/steering/conventions.md | CLAUDE.md ## Conventions |

**(b) constraint ↔ agent 규칙 파일 동기화 강제** -- 검토서 R2

constraint를 수정하면 agent 규칙 파일이 자동으로 재생성되어야 한다. 수동 재생성에 의존하면 양쪽 사이에 drift가 발생한다.

- constraint 파일 변경 → pre-commit hook이 agent 규칙 파일 재생성 여부 검사
- 불일치 시 커밋 차단 + "spec-recipe build 실행 필요" 메시지
- agent 규칙 파일 상단에 소스 constraint 해시 포함 → 불일치 기계적 감지

**(c) 미해결 피드백의 agent 규칙 인라인 주입** -- 검토서 R3

agent가 별도 feedback 파일을 "확인하는 행동"에 의존하지 않도록, 규칙 파일 재생성 시 미해결 HALT/BLOCK 항목을 상단에 직접 포함한다.

```markdown
# AGENTS.md (자동 생성)

## PENDING VIOLATIONS (자동 생성 - 교정 필요)
- HALT: INV-SEC-001 src/config.py:42 - 하드코딩된 시크릿
- BLOCK: PRC-TRC-001 src/handlers/payment.py - 추적성 태그 누락 3건

## Absolute Rules
...
```

이렇게 하면 agent가 규칙 파일을 로드하는 것만으로 미해결 위반을 인지한다.

### 2.3 피드백 루프 (Feedback Loop)

**현재 문제**: 검증 FAIL을 감지하지만 agent에게 돌아가지 않는다. 인간이 수동 전달.

**개선 방향**:

**(a) feedback/current.md 자동 관리**

검증 실행 시 위반 사항을 `.spec-recipe/feedback/current.md`에 자동 기록. 교정 후 재검증 PASS 시 자동 제거.

**(b) 계층별 게이트 동작**

| 계층 | 파일 저장 시 | 커밋 시 | CI 시 |
|------|------------|--------|-------|
| Invariant HALT | feedback 갱신 | **전체 커밋 차단** (미해결 HALT 존재 시) | 빌드 실패 |
| Principle BLOCK | - | **해당 파일 커밋 차단** | 빌드 실패 |
| Convention WARN | - | 로그 기록, 커밋 허용 | 경고 |

**(c) 교정 횟수 상한 + ESCALATE** -- 검토서 R4

agent가 교정을 시도했으나 반복 실패하는 경우 무한 루프를 방지한다.

```yaml
escalation:
  max_attempts: 3           # 동일 위반에 대한 교정 시도 상한
  on_exceed: escalate       # escalate | skip_with_log
  escalate_to: human        # human | senior_agent
```

feedback/current.md에 `attempts: 3/3, status: ESCALATE` 기록. ESCALATE 상태의 위반은 인간이 직접 해결해야 한다.

**(d) Watcher debounce** -- 검토서 R5

실시간 감시 시 파일 변경이 빈번하면 검증이 과도하게 실행된다.

- 마지막 변경 후 2초 대기 (debounce)
- Watcher는 invariant(fast depth)만 실행
- 나머지 검증은 커밋 시점으로 한정

### 2.4 측정 내장 (Metrics Embedded) -- 검토서 R7, R8, R9

**현재 문제**: 커버리지/복잡도 기준은 있으나, 하네스 성숙도 자체를 추적하지 않는다.

**개선 방향**: C(측정)를 A+B에서 분리하지 않고, 최소 측정 단위를 Phase 1부터 내장한다.

**(a) 검증 결과 누적**

```
.spec-recipe/
  metrics/
    runs/                    # 검증 실행 기록
      2026-03-28T10-30.json  # 타임스탬프별 결과
    summary.json             # 현재 상태 요약
```

매 검증 실행 시 결과를 JSON으로 누적한다.

**(b) 추적 지표**

| 지표 | 설명 | 수집 시점 |
|------|------|----------|
| invariant_violations | Invariant 위반 건수 | 매 커밋 |
| principle_compliance_rate | Principle 준수율 (%) | 매 커밋 |
| convention_compliance_rate | Convention 준수율 (%) | 매 커밋 |
| remediation_time_avg | 평균 교정 소요 시간 | 교정 완료 시 |
| remediation_attempts_avg | 평균 교정 시도 횟수 | 교정 완료 시 |
| escalation_count | ESCALATE 발생 건수 | ESCALATE 발생 시 |
| traceability_coverage | 추적성 태그 커버율 (%) | 매 커밋 |
| spec_code_drift_count | 스펙-코드 불일치 건수 | Feature 완료 시 |

**(c) 자동 리포트**

milestone 종료 시 또는 수동 호출 시 리포트 자동 생성:

```
spec-recipe report
  → .spec-recipe/metrics/ 데이터 기반
  → 추이 그래프 (텍스트 기반)
  → 반복 패턴 식별
  → 개선 제안 (장기: constraint 자동 조정)
```

---

## 3. 구현 Phase

### Phase 1: 제약 체계 + 주입 + 최소 측정

**범위**:
- constraints/ 디렉토리 구조 + YAML 스키마 (depth 필드 포함)
- 기본 invariant 7개 + principles 자동 변환 7개
- constraint 검증 엔진 (fast/normal depth)
- build.py 확장: constraint → agent 규칙 파일 변환 (AGENTS.md, CLAUDE.md)
- constraint ↔ agent 규칙 파일 동기화 검사 (pre-commit)
- metrics/ 디렉토리 + 기본 지표 수집

**산출물**:
- `.spec-recipe/constraints/` (invariants/, principles/, conventions/)
- `.spec-recipe/metrics/` (runs/, summary.json)
- build.py 확장
- init.py 확장 (constraint 초기화 + metrics 초기화)

### Phase 2: 피드백 루프 + 교정 강화

**범위**:
- feedback/ 디렉토리 + current.md 자동 관리
- pre-commit 확장: HALT/BLOCK/WARN 분기 + 미해결 HALT 전체 차단
- agent 규칙 파일에 미해결 위반 인라인 주입
- 교정 시도 상한 + ESCALATE 상태
- 교정 완료 시 metrics에 교정 소요 시간/시도 횟수 기록

**산출물**:
- `.spec-recipe/feedback/` (current.md, history/)
- pre-commit hook 확장
- 교정 추적 로직

### Phase 3: 고급 기능

**범위**:
- Watcher (fswatch/inotify + debounce + invariant fast 검증만)
- discover-conventions 명령어
- deep depth 검증 (외부 도구 연동)
- milestone 리포트 자동 생성
- 반복 패턴 분석 → constraint 제안 (Level 5 방향)
- Kiro hooks 형식 호환 (IDE 통합 가이드)

---

## 4. 검증 계획

각 Phase 완료 후 labor 프로젝트에서 실증한다.

| Phase | 실증 항목 | 성공 기준 |
|-------|----------|----------|
| Phase 1 | constraint 정의 + agent 규칙 파일 생성 + 기본 검증 | invariant 위반 시 커밋 차단 동작, agent 규칙 파일에 원칙 반영 확인 |
| Phase 2 | 의도적 위반 → 피드백 → 교정 → 재검증 | FAIL→feedback 기록→교정→PASS→feedback 제거의 전체 루프 동작 |
| Phase 3 | Watcher 실시간 감지, 리포트 생성 | 파일 저장 시 invariant 검증 동작, milestone 리포트 가독성 |

---

## 5. 미결 사항

| # | 항목 | 선택지 | 의견 |
|---|------|-------|------|
| M1 | Convention WARN → BLOCK 승격 임계값 | (a) 동일 WARN 3회 (b) 5회 (c) 사용자 설정 | (c) 사용자 설정 권고, 기본값 3회 |
| M2 | Invariant 사용자 비활성화 | (a) 완전 금지 (b) 명시적 사유 기재 시 허용 | (b) `override: explicit-only` |
| M3 | agent 규칙 파일 자동 재생성 트리거 | (a) pre-commit에서 검사만 (b) constraint 저장 시 자동 실행 | (a) 권고. 자동 실행은 의도치 않은 파일 변경 유발 |
| M4 | metrics 데이터 git 포함 여부 | (a) git 추적 (b) .gitignore | (a) 추적 권고. 팀 공유 + 추이 보존 |
| M5 | Phase 1 최소 agent 타겟 | (a) AGENTS.md만 (b) AGENTS.md + CLAUDE.md | (b) 2개 타겟으로 "동일 소스, 다른 출력" 검증 |
