# Harness Engineering Landscape 리서치 보고서

> 작성일: 2026-03-28
> 목적: AI agent 자율 개발에서의 harness engineering 도구 분석 및 spec-recipe 개선 방향 수립

---

## 1. Harness Engineering이란

OpenAI가 2026년 초 공식 명명한 개념. 전통적인 "test harness"(테스트 실행 환경)와 근본적으로 다르다.

**핵심 정의**: AI agent가 신뢰할 수 있는 코드를 생산하도록 환경, 제약, 피드백 루프, 문서 구조를 설계하는 엔지니어링 분야.

> "The model is commodity; the harness is the differentiator." -- NxCode

### 전통적 Test Harness vs. Agent Harness Engineering

| 구분 | Test Harness | Agent Harness Engineering |
|------|-------------|--------------------------|
| 대상 | 인간이 작성한 코드 검증 | AI agent의 코드 생산 환경 전체 |
| 범위 | 테스트 실행/리포트 | 스펙 전달 → 코드 생성 → 검증 → 피드백 루프 전체 |
| 핵심 관심사 | 코드가 맞는가? | agent가 올바른 코드를 만들 수 있는 환경인가? |
| 설계 대상 | 테스트 프레임워크 | 문서 구조, 제약 시스템, 컨텍스트 관리, 자동화 파이프라인 |

### OpenAI Harness Engineering 핵심 교훈 (Codex 내부 실험)

- 100만 줄 코드, 수동 작성 0줄. 1,500개 PR, 엔지니어 1인당 일일 3.5 PR.
- "AGENTS.md를 백과사전이 아닌 목차로 취급하라" -- 거대한 단일 지시 파일은 실패.
- docs/ 디렉토리를 시스템 오브 레코드로, AGENTS.md(~100줄)는 포인터 역할.
- agent-to-agent 리뷰로 인간 QA 병목 해소.
- worktree 단위 격리 실행 + 임시 관찰 스택(로그/메트릭).
- 6시간 이상의 단일 Codex 런이 일상적 (인간은 수면 중).

---

## 2. 주요 도구 분석

### 2.1 GitHub Spec Kit

| 항목 | 내용 |
|------|------|
| GitHub | github/spec-kit |
| Stars | ~83,000 |
| 성격 | 스펙 주도 개발 CLI 툴킷 |
| 지원 agent | Copilot, Claude Code, Gemini CLI, Cursor, Windsurf 외 20개+ |

**하네스 관점 핵심 요소**:
- `/speckit.constitution`: 프로젝트 거버닝 원칙 생성 (agent 행동 제약)
- `/speckit.specify`: what/why 중심 스펙 작성 (how는 agent에 위임)
- `/speckit.plan`: 기술 스택/아키텍처 선택 → 구현 계획 생성
- `/speckit.build`: 태스크 분해 → agent가 순차 구현
- Phase gate 방식: constitution → specify → plan → tasks → build

**하네스 강점**:
- 명확한 phase 분리로 agent의 scope creep 방지
- constitution이 모든 후속 단계의 제약으로 작동
- 에코시스템 최대 (커뮤니티 extensions, presets)

**한계**:
- 검증/피드백 루프는 agent 내부 판단에 의존 (기계적 강제 없음)
- phase gate는 슬래시 커맨드 기반이라 자동화 파이프라인 통합 약함
- brownfield(기존 프로젝트) 적용 가이드 부족

---

### 2.2 OpenSpec (Fission-AI)

| 항목 | 내용 |
|------|------|
| GitHub | Fission-AI/OpenSpec |
| Stars | ~35,000 |
| 성격 | 경량 스펙 프레임워크 (SDD for AI assistants) |
| 지원 agent | 20개+ AI 코딩 어시스턴트 |

**하네스 관점 핵심 요소**:
- `/opsx:propose` → 변경별 독립 폴더(proposal.md, specs/, design.md, tasks.md)
- `/opsx:apply` → 태스크 순차 구현
- `/opsx:verify` → 구현 결과 스펙 대비 검증
- `/opsx:archive` → 완료 후 아카이브, 스펙 갱신
- 아티팩트 기반 워크플로우 (change 단위 관리)

**하네스 강점**:
- "fluid not rigid" 철학 -- 엄격한 phase gate 없이 자유 반복
- brownfield 프로젝트에 강함 (기존 코드베이스 분석 → 스펙 생성)
- change 단위 격리가 agent의 컨텍스트 오염 방지에 효과적

**한계**:
- 검증이 semantic 수준 (agent의 자기 판단)
- 기계적 강제 메커니즘 없음
- 다중 agent 협업 시나리오 미지원

---

### 2.3 BMAD-METHOD

| 항목 | 내용 |
|------|------|
| GitHub | bmad-code-org/BMAD-METHOD |
| Stars | ~42,600 |
| 성격 | AI 에이전트 기반 애자일 개발 프레임워크 |
| 지원 agent | Claude Code, Cursor, 기타 IDE |

**하네스 관점 핵심 요소**:
- 12+ 전문 에이전트 페르소나 (PM, Architect, Developer, UX, Scrum Master 등)
- Party Mode: 다중 에이전트 페르소나를 한 세션에서 협업/토론
- Scale-Domain-Adaptive: 프로젝트 복잡도에 따라 계획 깊이 자동 조정
- 모듈 시스템: BMM(코어), BMB(빌더), TEA(테스트 아키텍트), BMGD(게임), CIS(창의)
- Edge Case Hunter: 코드 리뷰 시 경계 조건 탐지 병렬 실행

**하네스 강점**:
- SoC(관심사 분리)를 에이전트 레벨에서 실현 -- 구현자 ≠ 검증자
- 테스트 아키텍트 모듈(TEA)이 독립 검증 계층 제공
- 워크플로우가 34개+로 가장 포괄적
- bmad-help 스킬로 "다음에 뭘 해야 하는지" 자동 안내

**한계**:
- 복잡도 높음 -- 소규모 프로젝트에 과잉
- 기계적 검증보다 에이전트 간 대화 기반 검증 중심
- 페르소나 전환의 컨텍스트 비용

---

### 2.4 Agent OS (BuilderMethods)

| 항목 | 내용 |
|------|------|
| GitHub | buildermethods/agent-os |
| Stars | ~4,200 |
| 성격 | 코딩 표준 주입/관리 시스템 |
| 지원 agent | Claude Code, Cursor, Antigravity 등 (도구 무관) |

**하네스 관점 핵심 요소**:
- `/discover-standards`: 기존 코드베이스에서 패턴/컨벤션 자동 추출
- `/index-standards`: 표준 파일 인덱싱 + 탐지 규칙 생성
- `/deploy-standards`: 작업 컨텍스트에 맞는 표준 선택적 주입
- `/shape-spec`: 표준 기반 스펙 작성 가이드

**하네스 강점**:
- "표준 = 하네스의 레일"이라는 관점 -- agent에게 **어떻게** 코딩할지 주입
- 기존 코드베이스에서 표준을 추출하는 역방향 접근
- 토큰 효율성 고려 (표준을 간결하게 유지)
- 도구 완전 독립

**한계**:
- 스펙/계획 생성은 별도 도구에 의존
- 검증/피드백 루프 없음 (주입만 하고 결과 확인 안 함)
- 커뮤니티 규모 작음

---

### 2.5 Kiro (AWS)

| 항목 | 내용 |
|------|------|
| GitHub | kirodotdev/Kiro |
| Stars | ~3,300 (IDE 자체, 유료 사용자 별도) |
| 성격 | 스펙 주도 에이전틱 IDE (VSCode 기반) |
| 제공사 | AWS/Amazon |

**하네스 관점 핵심 요소**:
- **Specs**: 프롬프트 → 구조화된 스펙(요구사항 → 설계 → 태스크) 자동 변환
- **Steering**: .kiro/steering/ 마크다운 파일로 agent 행동 규칙 주입
- **Agent Hooks**: 파일 변경/이벤트에 반응하는 자동 트리거
  - 예: 코드 변경 → 자동 테스트 실행, 문서 변경 → 자동 sync
- **Powers**: 도메인별 컨텍스트/도구 확장

**하네스 강점**:
- Hooks가 가장 강력한 **자동 피드백 루프** 메커니즘
- Steering이 agent 행동의 기계적 제약으로 작동
- IDE 통합으로 개발자 경험 우수
- 스펙 → 코드 → 검증의 전체 루프가 IDE 안에서 완결

**한계**:
- IDE 종속 (Kiro 밖에서 사용 불가)
- 모델 선택 제한 (Claude 중심)
- 오픈소스이나 생태계가 AWS에 의존적
- 독립 CLI/CI 통합 제한적

---

### 2.6 AI Harness Scorecard

| 항목 | 내용 |
|------|------|
| GitHub | markmishaev76/ai-harness-scorecard |
| Stars | 14 (신규, 하지만 개념이 중요) |
| 성격 | 리포지토리 하네스 수준 평가 도구 |
| 근거 | DORA 2025, OpenAI Harness Engineering, SlopCodeBench, Kent Beck |

**하네스 관점 핵심 요소**:
- 5개 카테고리, 31개 체크, A~F 등급
  1. **Architectural Docs** (20%): 아키텍처 문서, agent 지시, ADR
  2. **Mechanical Constraints** (25%): CI, 린터, 타입 안전, 의존성 감사
  3. **Testing & Stability** (25%): 테스트, 커버리지, 뮤테이션, 퍼즈
  4. **Review & Drift** (15%): 코드 리뷰 강제, stale doc 탐지
  5. **AI-Specific Safeguards** (15%): AI 사용 규범, 소규모 배치, 에러 처리

**하네스 강점**:
- "리포가 agent에게 준비됐는가?"가 아닌 "agent가 여기서 만들 코드가 신뢰 가능한가?" 관점
- 정량적 측정 (점수화)
- CI/CD GitHub Action 통합
- 연구 기반 체크리스트 (DORA, SlopCodeBench)

**한계**:
- 평가만 하고 교정은 안 함
- 스타 수 낮음 (인지도 부족)
- 스펙 주도 개발과의 직접 연결 없음

---

### 2.7 Open Harness

| 항목 | 내용 |
|------|------|
| GitHub | MaxGfeller/open-harness |
| Stars | ~209 |
| 성격 | Agent harness 프로그래밍 라이브러리 (TypeScript) |
| 기반 | Vercel AI SDK |

**하네스 관점 핵심 요소**:
- Agent 클래스: 모델 + 도구 + 멀티스텝 실행 루프 래핑
- Subagent 시스템: 부모 agent가 자식 agent에게 태스크 위임 (병렬)
- 모델 무관: AI SDK 호환 모든 프로바이더 사용
- 이벤트 스트리밍: text delta, tool call, step completion 등 타입 이벤트

**하네스 강점**:
- "하네스를 코드로 작성하는" 접근 -- 가장 유연
- subagent 패턴이 Claude Code/Codex의 위임 구조를 재현
- 경량 (서버/스레드 관리 불필요)
- 커스텀 agent 파이프라인 구축에 최적

**한계**:
- 스펙 주도 개발 기능 없음 (순수 런타임 하네스)
- 문서/표준 관리 계층 없음
- 초기 단계 프로젝트

---

### 2.8 Hive (Aden)

| 항목 | 내용 |
|------|------|
| GitHub | aden-hive/hive |
| Stars | ~9,900 |
| 성격 | 목표 주도 agent 개발 프레임워크 + 런타임 하네스 |
| 투자 | Y Combinator |

**하네스 관점 핵심 요소**:
- Queen Agent: 자연어 목표 → agent 그래프 + 연결 코드 자동 생성
- Self-Improving Agent: 실행 결과 기반 자기 개선
- Multi-Agent 시스템: agent 간 협업 오케스트레이션
- Headless 개발: UI 없이 agent만으로 개발
- Human-in-the-Loop: 필요 시 인간 개입 지점
- MCP 102개 도구 통합

**하네스 강점**:
- "목표를 말하면 agent 시스템을 만들어주는" 메타 하네스
- 자기 개선 루프 내장
- 프로덕션 런타임으로 사용 가능

**한계**:
- 스펙 주도 개발보다 목표 주도(outcome-driven) 지향
- 프레임워크 종속도 높음
- 복잡도 높음

---

### 2.9 AI-Rule-Spec (aicodingrules.org)

| 항목 | 내용 |
|------|------|
| 사이트 | aicodingrules.org |
| 성격 | AI 코딩 에이전트 규칙 통합 표준 제안 |
| 상태 | 표준화 제안 단계 |

**하네스 관점 핵심 요소**:
- Rule Definition Language (RDL): YAML 메타데이터 + Markdown 본문
- 계층적 규칙: user → org → project 우선순위
- 모듈/조합 가능: 작은 규칙 컴포넌트 조합
- 도구 무관 표준: Cursor, Copilot, Claude Code 등 규칙 형식 통일

**하네스 관점 의의**:
- 현재 도구별 규칙 파편화 문제를 정면으로 다룸
- 하네스의 "제약 계층"을 표준화하려는 시도
- spec-recipe의 코어 원칙 배포 형식에 참고 가능

---

### 2.10 OpenDev (arxiv 2603.05344)

| 항목 | 내용 |
|------|------|
| 출처 | arxiv 2603.05344 (학술 논문) |
| 성격 | 터미널 네이티브 코딩 에이전트 기술 보고서 |

**하네스 아키텍처 정의 (학술적)**:
- **Scaffolding**: agent 실행 전 조립 (시스템 프롬프트, 도구 스키마, subagent 레지스트리)
- **Harness**: 런타임 오케스트레이션 (도구 디스패치, 컨텍스트 관리, 안전 강제)
- Dual-agent 아키텍처: Planning agent(읽기 전용) / Execution agent(읽기+쓰기)
- 적응형 컨텍스트 압축: 오래된 관찰을 점진적으로 축소
- 자동 메모리 시스템: 세션 간 프로젝트 지식 축적
- 이벤트 주도 시스템 리마인더: instruction fade-out 대응

---

## 3. 도구 간 비교 매트릭스

| 도구 | Stars | 스펙관리 | 제약주입 | 검증/피드백 | 자동화 | agent 독립 | 기계적 강제 |
|------|-------|---------|---------|------------|--------|-----------|------------|
| Spec Kit | 83K | **강** | 중 (constitution) | 약 | 중 (CLI) | **강** | 약 |
| OpenSpec | 35K | **강** | 약 | 중 (verify) | 중 | **강** | 약 |
| BMAD | 43K | **강** | 중 (personas) | 중 (TEA) | 중 | 중 | 약 |
| Agent OS | 4K | 약 | **강** (standards) | 약 | 중 | **강** | 약 |
| Kiro | 3K | **강** | **강** (steering) | **강** (hooks) | **강** | 약 (IDE 종속) | **중** |
| Scorecard | 14 | 약 | 약 | **강** (평가) | **강** (CI) | **강** | **강** |
| Open Harness | 209 | 없음 | 없음 | 없음 | **강** (코드) | **강** | 없음 |
| Hive | 10K | 약 | 중 | 중 (self-improve) | **강** | 약 (프레임워크) | 약 |
| AI-Rule-Spec | - | 없음 | **강** (표준) | 약 | 약 | **강** | 중 |
| OpenDev(논문) | - | 없음 | 중 | 중 | **강** | N/A | 중 |

---

## 4. Harness Engineering의 핵심 레이어 (종합)

리서치를 통해 도출한 agent harness의 구성 레이어:

```
┌─────────────────────────────────────────────┐
│  L5. Evaluation (평가/측정)                    │  ← Scorecard, DORA
│  리포 하네스 수준 측정, 점수화, 트렌드 추적        │
├─────────────────────────────────────────────┤
│  L4. Feedback Loop (피드백 루프)               │  ← Kiro Hooks, CI/CD
│  FAIL → 자동 재시도, agent 간 리뷰, 자기 수정     │
├─────────────────────────────────────────────┤
│  L3. Verification (검증)                      │  ← spec-recipe v0.8, Scorecard
│  스펙↔코드↔테스트 일치 검사, 기계적 PASS/FAIL    │
├─────────────────────────────────────────────┤
│  L2. Constraint Injection (제약 주입)          │  ← Agent OS, Kiro Steering, AI-Rule-Spec
│  표준/규칙/constitution을 agent 컨텍스트에 주입   │
├─────────────────────────────────────────────┤
│  L1. Spec Management (스펙 관리)              │  ← Spec Kit, OpenSpec, BMAD
│  요구사항 → 스펙 → 계획 → 태스크 분해            │
├─────────────────────────────────────────────┤
│  L0. Runtime Harness (런타임)                 │  ← Open Harness, Hive, OpenDev
│  agent 실행 루프, 도구 디스패치, 컨텍스트 관리     │
└─────────────────────────────────────────────┘
```

---

## 5. spec-recipe 현재 위치 평가

### 이미 갖춰진 것
- L1(스펙 관리): 코어 원칙, 구조, 프로세스, 용어집
- L3(검증): 구조/추적성/계약 검증 스크립트, pre-commit hook
- 빌드 시스템: 코어 → 타겟(spec-kit, bmad) 변환

### 부족한 것
- **L2(제약 주입)**: 코어 원칙이 agent 컨텍스트에 실제로 주입되는 메커니즘 없음
- **L4(피드백 루프)**: FAIL 후 자동 재시도/교정 루프 미구현
- **L5(평가)**: 하네스 수준 측정 없음
- **L0(런타임)**: agent 실행 환경 자체에 대한 관여 없음

### 핵심 gap
1. **spec-recipe는 L1+L3에 집중** -- 스펙은 잘 만들지만 agent에게 전달하는 방법이 없음
2. **검증 결과가 agent에게 돌아가지 않음** -- FAIL을 감지하지만 agent가 고치는 루프가 없음
3. **agent 도구 생태계와 단절** -- Spec Kit/OpenSpec/Kiro 등과 통합점 없음

---

## 6. 개선 방향 제안 (승인 대기)

### 방향 A: "코어를 agent에게 전달하는 파이프라인" (L2 강화)
- 코어 원칙 → agent 규칙 형식(AGENTS.md, .cursor/rules, steering) 자동 변환
- AI-Rule-Spec 호환 형식 지원
- Agent OS의 "표준 주입" 패턴 차용

### 방향 B: "검증-교정 피드백 루프" (L4 구축)
- 검증 FAIL → agent에게 diff + 교정 지시 자동 전달
- Kiro Hooks 패턴 차용 (파일 변경 → 자동 검증 트리거)
- pre-commit 결과를 agent 컨텍스트에 재주입

### 방향 C: "하네스 수준 측정" (L5 신설)
- Scorecard 방식으로 프로젝트 하네스 성숙도 점수화
- spec-recipe 고유 체크: 추적성 태그 비율, 용어집 준수율, drift 감지
- CI 통합 가능한 리포트

### 방향 D: "타겟 생태계 확장" (기존 도구 통합)
- build.py에 Kiro steering 타겟 추가
- OpenSpec 아티팩트 형식 호환
- AI-Rule-Spec 표준 준수

### 우선순위 제안
1. **A + B** (제약 주입 + 피드백 루프) -- 가장 큰 gap이자 가장 높은 임팩트
2. **D** (타겟 확장) -- 생태계 연결
3. **C** (측정) -- 장기적

---

## 7. 참고 자료

- OpenAI Harness Engineering: https://openai.com/index/harness-engineering/
- GitHub Spec Kit: https://github.com/github/spec-kit
- OpenSpec: https://github.com/Fission-AI/OpenSpec
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
- Agent OS: https://github.com/buildermethods/agent-os
- Kiro: https://github.com/kirodotdev/Kiro
- AI Harness Scorecard: https://github.com/markmishaev76/ai-harness-scorecard
- Open Harness: https://github.com/MaxGfeller/open-harness
- Hive: https://github.com/aden-hive/hive
- AI-Rule-Spec: https://aicodingrules.org/
- OpenDev 논문: https://arxiv.org/html/2603.05344v1
- Martin Fowler SDD 분석: https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- DORA 2025: https://dora.dev/research/2025/dora-report
