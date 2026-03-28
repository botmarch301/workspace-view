# 설계안: 제약 주입(L2) + 피드백 루프(L4)

> 작성일: 2026-03-28
> 근거: harness-engineering-landscape.md 리서치 결과
> 대상: spec-recipe v0.9.0 (가칭)
> 상태: 설계 제안 (승인 대기)

---

## 0. 설계 원칙

> "준수되지 않으면 산출물이 아닌 쓰레기를 만들 수 있다"

1. **강제는 가이드라인이 아닌 게이트**: 원칙 위반 시 작업이 진행되지 않아야 한다
2. **보안부터 컨벤션까지 계층적**: 절대 불변 원칙과 프로젝트별 확장 원칙을 분리
3. **agent 독립**: 특정 agent(Claude Code, Cursor, Codex 등)에 종속되지 않는다
4. **기계적 강제 우선**: agent의 "이해"에 의존하지 않고 스크립트로 차단한다

---

## 1. 현재 Gap 분석

### spec-recipe가 이미 가진 것
- 원칙(principles.md): 7개 핵심 원칙 정의
- 검증(verification.md): 25+개 기계적 체크 정의
- 검증 프레임워크(verification-framework.md): 3-way 계약, 어댑터 인터페이스
- pre-commit hook: 커밋 시 검증 실행
- 교정 사이클: FAIL → 교정 계획 → 교정 → 재검증 프로세스 정의

### 빠져 있는 것

| Gap | 설명 | 영향 |
|-----|------|------|
| **G1. 원칙 → agent 전달 파이프라인** | principles.md가 존재하지만 agent 컨텍스트에 주입되지 않음 | agent가 원칙을 모른 채 코드 생성 |
| **G2. 계층적 제약 체계** | 보안 원칙과 컨벤션이 같은 레벨에 혼재 | 우선순위 구분 불가, 사용자 확장 어려움 |
| **G3. 실시간 피드백 루프** | pre-commit은 커밋 시점에만 작동 | 커밋 전 작업 중 위반 누적 |
| **G4. FAIL → agent 자동 재주입** | FAIL 감지는 하지만 agent에게 돌아가지 않음 | 인간이 수동으로 FAIL 내용을 agent에게 전달해야 함 |
| **G5. agent 규칙 파일 생성** | AGENTS.md, .cursor/rules, steering 등 미생성 | 기존 생태계 도구와 단절 |

---

## 2. 제약 주입 설계 (L2: Constraint Injection)

### 2.1 제약 계층 모델

OpenAI의 AGENTS.md 계층 + Kiro의 Steering + Agent OS의 Standards에서 차용.

```
┌──────────────────────────────────────────────┐
│  L2-C. Convention (컨벤션)                     │  사용자 정의, 프로젝트별
│  파일명 규칙, 코드 스타일, 커밋 메시지 형식      │  위반 시: WARNING → 교정 요청
├──────────────────────────────────────────────┤
│  L2-B. Principle (원칙)                        │  spec-recipe 코어, 프로젝트 공통
│  Spec-First, SoC, Traceability, Drift 방지    │  위반 시: BLOCK → 커밋 차단
├──────────────────────────────────────────────┤
│  L2-A. Invariant (불변 규칙)                   │  절대 위반 불가
│  보안 정책, 인증 규칙, 데이터 보호, 라이선스     │  위반 시: HALT → 작업 즉시 중단
└──────────────────────────────────────────────┘
```

**핵심**: 각 계층의 위반 시 대응이 다르다.

| 계층 | 위반 대응 | 유예 가능 | 예시 |
|------|----------|----------|------|
| **Invariant** | HALT (즉시 중단) | 불가 | API 키 하드코딩 금지, SQL 인젝션 패턴 금지 |
| **Principle** | BLOCK (커밋 차단) | Milestone 단위 유예 | 추적성 태그 누락, 스펙 없는 기능 구현 |
| **Convention** | WARN (경고 + 교정 요청) | 자유 | 파일명 규칙, 주석 형식 |

### 2.2 제약 정의 형식

AI-Rule-Spec에서 영감받은 YAML + Markdown 하이브리드.

```yaml
# .spec-recipe/constraints/invariants/no-hardcoded-secrets.yml
id: INV-SEC-001
layer: invariant          # invariant | principle | convention
name: "하드코딩된 시크릿 금지"
severity: halt
scope:
  files: "**/*.{py,js,ts,java,go,rs}"
  exclude: ["**/test/**", "**/*_test.*"]

detection:
  method: "regex"         # regex | ast | script | tool
  patterns:
    - 'password\s*=\s*["\'][^"\']{8,}'
    - 'api[_-]?key\s*=\s*["\'][A-Za-z0-9]{16,}'
    - 'secret\s*=\s*["\'][^"\']{8,}'
    - 'token\s*=\s*["\'](?!{)[^"\']{16,}'
  
enforcement:
  pre_commit: true        # 커밋 시 차단
  on_save: true           # 저장 시 경고 (IDE 통합 시)
  ci: true                # CI에서 차단

remediation: |
  시크릿은 환경변수 또는 시크릿 매니저를 통해 주입해야 합니다.
  - 환경변수: `os.environ['API_KEY']`
  - .env 파일 + .gitignore
  - 시크릿 매니저 (AWS SM, Vault 등)
```

### 2.3 사용자 확장 구조

```
.spec-recipe/
  constraints/
    invariants/         # 절대 규칙 (spec-recipe 코어 제공 + 사용자 추가)
      no-hardcoded-secrets.yml
      no-sql-injection.yml
      no-eval-exec.yml
      custom-security.yml       # 사용자 추가
    principles/         # 코어 원칙 (spec-recipe 코어에서 자동 생성)
      spec-first.yml
      traceability.yml
      separation-of-concerns.yml
    conventions/        # 컨벤션 (사용자 정의)
      file-naming.yml
      commit-message.yml
      code-style.yml
    index.yml           # 전체 제약 인덱스 (자동 생성)
```

**초기화 시 동작** (`spec-recipe init`):
1. invariants/ 에 기본 보안 규칙 세트 생성 (7개)
2. principles/ 에 코어 원칙에서 자동 변환 (7개)
3. conventions/ 는 빈 디렉토리 + 템플릿 제공
4. index.yml 자동 생성

### 2.4 Agent 규칙 파일 생성 (build.py 확장)

코어 제약 → agent별 규칙 파일로 변환:

| 코어 제약 | Codex (AGENTS.md) | Cursor (.cursor/rules/) | Kiro (.kiro/steering/) | Claude Code (CLAUDE.md) |
|----------|-------------------|------------------------|----------------------|----------------------|
| invariants/ | ## Absolute Rules | security.md (Always) | security.md | ## Security Rules |
| principles/ | ## Development Principles | principles.md (Always) | standards.md | ## Principles |
| conventions/ | ## Conventions | style.md (Auto) | conventions.md | ## Conventions |

```python
# build.py 확장 의사코드
def build_agent_rules(constraints_dir, target):
    constraints = load_all_constraints(constraints_dir)
    
    if target == "codex":
        return render_agents_md(constraints)
    elif target == "cursor":
        return render_cursor_rules(constraints)
    elif target == "kiro":
        return render_kiro_steering(constraints)
    elif target == "claude-code":
        return render_claude_md(constraints)
```

---

## 3. 피드백 루프 설계 (L4: Feedback Loop)

### 3.1 피드백 루프 아키텍처

Kiro Hooks의 이벤트 트리거 + OpenAI의 agent-to-agent 리뷰에서 차용.

```
Agent 작업    →  파일 변경  →  검증 트리거  →  결과 판정  →  피드백 주입
   │                              │                           │
   │                         ┌────┴────┐                      │
   │                         │ Watcher │                      │
   │                         └────┬────┘                      │
   │                              │                           │
   │                    ┌─────────┴─────────┐                 │
   │                    │  Constraint Check  │                 │
   │                    │  + Verification    │                 │
   │                    └─────────┬─────────┘                 │
   │                              │                           │
   │                    ┌─────────┴─────────┐                 │
   │                    │  PASS → 계속      │                 │
   │                    │  WARN → 경고 파일  │──────────────→ │
   │                    │  BLOCK → 차단 파일 │──────────────→ │
   │                    │  HALT → 즉시 중단  │──────────────→ │
   │                    └───────────────────┘                 │
   │                                                          │
   ←──────────────────────────────────────────────────────────┘
         피드백 파일(.spec-recipe/feedback/)을 통해 재주입
```

### 3.2 피드백 채널 (agent 독립)

핵심 문제: agent에게 "피드백을 전달하는 방법"은 agent마다 다르다.

**해결: 피드백 파일 기반 + agent 규칙에 "피드백 파일 확인" 지시 포함**

```
.spec-recipe/
  feedback/
    current.md          # 현재 미해결 피드백 (agent가 매 작업 전 확인)
    history/            # 해결된 피드백 아카이브
```

```markdown
# .spec-recipe/feedback/current.md
# Pending Feedback (자동 생성 - 수동 수정 금지)

## HALT: INV-SEC-001 하드코딩된 시크릿 감지
- **파일**: src/config.py:42
- **감지**: `api_key = "sk-abc123..."`
- **교정**: 환경변수 `os.environ['API_KEY']`로 교체
- **상태**: 미해결
- **생성**: 2026-03-28T10:30:00

## BLOCK: PRC-TRC-001 추적성 태그 누락
- **파일**: src/handlers/payment.py
- **감지**: 함수 3개에 `Implements:` 태그 없음
- **교정**: 해당 함수에 스펙 ID 태깅 필요
- **상태**: 미해결
- **생성**: 2026-03-28T10:30:00
```

**Agent 규칙에 자동 삽입되는 피드백 확인 지시:**

```markdown
## Feedback Check (자동 생성)
작업 시작 전 반드시 `.spec-recipe/feedback/current.md`를 확인하세요.
- HALT 항목이 있으면 해당 항목부터 교정합니다.
- BLOCK 항목이 있으면 관련 파일 수정 시 함께 교정합니다.
- WARN 항목은 관련 작업 시 참고합니다.
미해결 HALT가 있는 상태에서 다른 작업을 진행하지 마세요.
```

### 3.3 검증 트리거 시점

| 트리거 | 실행 검증 | 피드백 방식 | 구현 방법 |
|--------|----------|------------|----------|
| **파일 저장 시** | Invariant만 (경량) | feedback/current.md 갱신 | fswatch / inotify |
| **커밋 시** | Invariant + Principle + Convention | pre-commit 차단 + feedback 갱신 | git hook |
| **PR/Push 시** | 전체 검증 | CI 리포트 + feedback 갱신 | CI action |
| **수동 호출** | 지정 범위 | 콘솔 출력 + feedback 갱신 | CLI 명령어 |

### 3.4 자동 교정 루프

```
검증 FAIL
    │
    ├─ HALT → feedback/current.md에 기록
    │         agent 규칙에 "HALT 우선 교정" 포함
    │         pre-commit에서 HALT 미해결 시 모든 커밋 차단
    │
    ├─ BLOCK → feedback/current.md에 기록
    │          해당 파일 커밋 시 차단
    │          교정 후 재검증 → PASS 시 feedback에서 제거
    │
    └─ WARN → feedback/current.md에 기록
              커밋 허용, 로그 기록
              Convention 위반 카운트 추적 (임계값 초과 시 BLOCK 승격)
```

---

## 4. 통합: 제약 주입 + 피드백 루프 = Enforcement Harness

### 4.1 전체 흐름

```
┌──────────────────────────────────────────────────────────┐
│                    spec-recipe init                       │
│  1. constraints/ 디렉토리 생성 (invariant/principle/conv) │
│  2. 기본 invariant 규칙 세트 생성                          │
│  3. 코어 principles → constraint YAML 자동 변환            │
│  4. agent 규칙 파일 생성 (AGENTS.md 등)                    │
│  5. pre-commit hook 설치 (constraint 검증 포함)            │
│  6. feedback/ 디렉토리 초기화                              │
└──────────────────────────────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────┐
│                   Agent 작업 시작                          │
│  1. Agent가 규칙 파일(AGENTS.md 등) 자동 로드              │
│     → 코어 원칙 + 보안 규칙 + 컨벤션 인지                  │
│  2. feedback/current.md 확인                              │
│     → 미해결 HALT가 있으면 교정 우선                       │
│  3. 코드 생성/수정                                        │
└──────────────────────────────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────┐
│                 파일 변경 감지 (Watcher)                    │
│  1. Invariant 검증 실행 (밀리초 단위, 경량)                 │
│  2. HALT 감지 시 → feedback/current.md 즉시 갱신           │
│  3. Agent가 다음 작업 시 feedback 확인                     │
└──────────────────────────────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────┐
│                    커밋 시 (pre-commit)                    │
│  1. 미해결 HALT 존재 → 전체 커밋 차단                      │
│  2. Invariant + Principle + Convention 전체 검증           │
│  3. BLOCK 위반 → 해당 파일 커밋 차단                       │
│  4. WARN → 로그 기록, 커밋 허용                            │
│  5. 결과 → feedback/current.md 갱신                       │
└──────────────────────────────────────────────────────────┘
                           │
                           v
┌──────────────────────────────────────────────────────────┐
│                    교정 → 재검증 루프                      │
│  Agent가 feedback/current.md 읽고 교정                    │
│  → 파일 저장 → Watcher 재검증 → PASS → feedback에서 제거  │
│  → FAIL → feedback 갱신 → Agent 재교정                    │
└──────────────────────────────────────────────────────────┘
```

### 4.2 구현 범위 (v0.9.0)

**Phase 1: 제약 체계 + 기본 주입** (핵심)
- [ ] constraints/ 디렉토리 구조 + YAML 스키마 정의
- [ ] 기본 invariant 규칙 세트 (보안 7개)
- [ ] principles.md → constraint YAML 자동 변환
- [ ] init.py 확장: constraint 초기화
- [ ] build.py 확장: constraint → AGENTS.md/CLAUDE.md 변환

**Phase 2: 피드백 루프** (핵심)
- [ ] feedback/ 디렉토리 + current.md 자동 관리
- [ ] constraint 검증 엔진 (YAML 규칙 → 검증 실행)
- [ ] pre-commit hook 확장: constraint 검증 + HALT/BLOCK/WARN 분기
- [ ] agent 규칙에 feedback 확인 지시 자동 삽입

**Phase 3: 실시간 감시** (선택적)
- [ ] fswatch/inotify 기반 파일 변경 감시 데몬
- [ ] Invariant 실시간 검증 (저장 시)
- [ ] IDE 통합 가이드 (Kiro hooks 형식 호환)

---

## 5. 경쟁 도구 대비 차별점

| 특성 | Spec Kit | Kiro | Agent OS | spec-recipe (제안) |
|------|----------|------|----------|-------------------|
| 원칙 정의 | constitution (평문) | steering (평문) | standards (평문) | **계층적 YAML** (INV/PRC/CONV) |
| 위반 대응 | 없음 (가이드만) | hooks (IDE 종속) | 없음 (주입만) | **HALT/BLOCK/WARN 분기** |
| 피드백 루프 | 없음 | hooks → agent | 없음 | **파일 기반 (agent 독립)** |
| 기계적 강제 | 없음 | 부분 (hook) | 없음 | **pre-commit + watcher** |
| 사용자 확장 | extension | steering 파일 | standards 파일 | **constraints/ 디렉토리** |
| agent 독립 | O | X (IDE) | O | **O** |

**spec-recipe의 고유 가치**: 
"원칙을 선언하고 → agent에게 주입하고 → 기계적으로 강제하고 → 위반 시 자동 피드백"의 **전 구간 파이프라인**을 agent 독립적으로 제공하는 유일한 프레임워크.

---

## 6. 기본 제공 Invariant 규칙 (초안)

| ID | 이름 | 감지 방법 | 대상 |
|----|------|----------|------|
| INV-SEC-001 | 하드코딩된 시크릿 | regex | 모든 소스 |
| INV-SEC-002 | SQL 인젝션 패턴 | regex + AST | Python, JS, Java |
| INV-SEC-003 | eval/exec 사용 금지 | regex | Python, JS |
| INV-SEC-004 | 안전하지 않은 역직렬화 | regex | Python (pickle), Java |
| INV-SEC-005 | 평문 HTTP 엔드포인트 | regex | 설정 파일 |
| INV-SEC-006 | 과도한 권한 요청 | regex | IAM/권한 설정 파일 |
| INV-SEC-007 | 디버그 모드 프로덕션 노출 | regex | 설정 파일 |

---

## 7. 미결 사항 (논의 필요)

1. **Convention WARN → BLOCK 승격 임계값**: 동일 WARN 몇 회 반복 시 BLOCK으로 승격할지?
2. **Invariant 사용자 비활성화 허용 여부**: 보안 규칙도 사용자가 끌 수 있어야 하는지? (제안: `override: explicit-only`로 명시적 사유 기재 시에만 허용)
3. **Watcher 데몬의 리소스 비용**: 대규모 프로젝트에서 fswatch 성능. (제안: invariant만 실시간, 나머지는 커밋 시)
4. **CI 통합 형식**: GitHub Actions, GitLab CI 등 구체적 YAML 템플릿 범위
