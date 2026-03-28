# Harness Engineering 도구 수집 목록

> 수집일: 2026-03-28
> 수집 방법: GitHub API 검색 (harness engineering, agent harness, coding agent, spec driven development, agentic development 등 키워드 조합)
> 수집 대상: GitHub 공개 저장소 중 harness engineering 관련 도구/프레임워크/템플릿
> 총 수집: 85개 저장소 검토 → 8개 선별 (대중화 5 + 주시 3)

---

## 선별 기준

**대중화 도구 (5개)**: Stars 20 이상, 실질적 코드/문서가 있는 도구성 저장소, 고유한 접근 방식 보유
**주시 도구 (3개)**: Stars 무관, 기존 도구에 없는 독특한 관점이나 기능 보유

**공통 탈락 사유**:
- 학습 가이드/노트 수집용 (도구 아님)
- awesome list (큐레이션만, 도구 아님)
- 템플릿/보일러플레이트 (고유 기능 없음)
- README만 있고 실질적 구현 없음
- 다른 도구의 포크/재포장

---

## 선별된 도구 (8개)

### 대중화 도구 (5개) — 하네스 역할을 수행하는 대형 도구 포함

| # | 이름 | URL | Stars | 요약 | 선별 이유 |
|---|------|-----|-------|------|----------|
| 1 | Spec Kit (GitHub) | https://github.com/github/spec-kit | 83,000+ | 스펙 주도 개발 CLI 툴킷. constitution → specify → plan → build 단계. | 최대 에코시스템. constitution이 하네스의 "제약 주입" 역할 수행. 20+ 에이전트 지원. |
| 2 | BMAD-METHOD | https://github.com/bmad-code-org/BMAD-METHOD | 42,600+ | AI 에이전트 기반 애자일 개발 프레임워크. 12+ 전문 페르소나. | 관심사 분리를 에이전트 레벨에서 구현. TEA(테스트 아키텍트)가 독립 검증 계층 제공. |
| 3 | OpenSpec (Fission-AI) | https://github.com/Fission-AI/OpenSpec | 35,000+ | 경량 스펙 프레임워크. change 단위 격리. | brownfield에 가장 강함. change 단위 격리가 컨텍스트 오염 방지에 효과적. |
| 4 | Hive (Aden) | https://github.com/aden-hive/hive | 9,900+ | 목표 주도 에이전트 프레임워크 + 런타임 하네스. YC 투자. | 자기 개선 루프 내장. 메타 하네스 (목표 → 에이전트 시스템 자동 생성). |
| 5 | Kiro (AWS) | https://github.com/kirodotdev/Kiro | 3,300+ | 스펙 주도 에이전틱 IDE. Steering + Hooks. | IDE 안에서 L1~L4 완결. Hooks가 가장 강력한 자동 피드백 루프 메커니즘. |

### 주시 도구 (3개) — 하네스 전용, 독특한 관점

| # | 이름 | URL | Stars | 요약 | 선별 이유 |
|---|------|-----|-------|------|----------|
| 6 | Entrix | https://github.com/phodal/entrix | 31 | 품질 규칙을 실행 가능한 가드레일로 변환. tier별 검증(fast/normal/deep). | 기계적 강제를 가장 직접적으로 구현. L2~L4를 단일 도구로 커버하는 유일한 사례. |
| 7 | AI Harness Scorecard | https://github.com/markmishaev76/ai-harness-scorecard | 14 | 리포의 하네스 수준을 A~F로 정량 평가. 31개 체크, 연구 기반. | "하네스를 측정하는" 유일한 도구. DORA 2025 + OpenAI + SlopCodeBench 근거. |
| 8 | Reins | https://github.com/WellDunDun/reins | 6 | scaffold → audit → evolve → doctor 4단계 CLI. 의존성 0개. | "방법론을 도구로" 변환. brownfield 즉시 적용. 점진적 하네스 도입에 최적. |

---

## 탈락 목록 (주요)

| 이름 | URL | Stars | 요약 | 탈락 사유 |
|------|-----|-------|------|----------|
| AltimateAI/altimate-code | https://github.com/AltimateAI/altimate-code | 423 | dbt/SQL/데이터 웨어하우스용 에이전틱 데이터 엔지니어링 하네스 | 데이터 엔지니어링 특화. 일반 코딩 에이전트 하네스가 아님 |
| AIxCyberChallenge/sherpa | https://github.com/AIxCyberChallenge/sherpa | 121 | 보안 하네스 엔지니어링. 프로그램 분석용 | 보안 분석 특화. 일반 소프트웨어 개발 하네스가 아님 |
| deusyu/harness-engineering | https://github.com/deusyu/harness-engineering | 150 | Harness Engineering 학습 가이드 | 학습 노트/가이드. 도구가 아님 |
| alirezarezvani/claude-code-tresor | https://github.com/alirezarezvani/claude-code-tresor | 650 | Claude Code 유틸리티 모음 (스킬, 에이전트, 슬래시 커맨드, 프롬프트) | 유틸리티 모음집. 하네스 엔지니어링 도구가 아닌 일반 Claude Code 확장 |
| dsifry/metaswarm | https://github.com/dsifry/metaswarm | 159 | 멀티 에이전트 오케스트레이션 프레임워크 (Claude Code, Gemini CLI, Codex CLI) | 오케스트레이션 프레임워크. 하네스 엔지니어링보다는 에이전트 관리에 가까움 |
| bgdnvk/clanker | https://github.com/bgdnvk/clanker | 223 | 자율 시스템 엔지니어링 CLI 에이전트 (AWS, GCP, Cloud 등) | 클라우드 인프라 자동화 에이전트. 소프트웨어 개발 하네스가 아님 |
| AutoJunjie/awesome-agent-harness | https://github.com/AutoJunjie/awesome-agent-harness | 181 | Agent harness awesome list | awesome list. 도구가 아님 |
| jiji262/awesome-harness-engineering | https://github.com/jiji262/awesome-harness-engineering | 11 | Harness Engineering 리소스 awesome list | awesome list. 도구가 아님 |
| OndrejDrapalik/gmux | https://github.com/OndrejDrapalik/gmux | 44 | Ghostty x tmux 터미널 레이어 | 터미널 도구. 하네스 엔지니어링 도구가 아닌 개발 환경 유틸리티 |
| alchemiststudiosDOTai/harness-engineering | https://github.com/alchemiststudiosDOTai/harness-engineering | 81 | 하네스 엔지니어링 토론/문서 저장소 | 토론/문서 저장소. 실행 가능한 도구가 아님 |
| BulloRosso/etienne | https://github.com/BulloRosso/etienne | 19 | 커스텀 AI 에이전트를 위한 코딩 에이전트 하네스 | 비즈니스 협업자 에이전트(비기술 사용자 대상). 개발자용 하네스가 아님 |
| lipingtababa/agents-zone-skillset | https://github.com/lipingtababa/agents-zone-skillset | 14 | Harness Engineering Playbook 구현 스킬셋 | playbook의 부속품. 독립 도구가 아님 |
| martinsson/harness-engineering-kata | https://github.com/martinsson/harness-engineering-kata | 12 | 하네스 엔지니어링 연습(kata) | 학습/연습용. 도구가 아님 |
| broomva/harness-engineering | https://github.com/broomva/harness-engineering | 12 | Harness Engineering playbook 구현 | lipingtababa 계열 playbook 재구현. 차별점 부족 |
| Phlegonlabs/Harness-Engineering-skills | https://github.com/Phlegonlabs/Harness-Engineering-skills | 12 | Claude/Codex용 AI 네이티브 엔지니어링 워크플로우 스킬 | 스킬 모음. 독립 도구가 아님 |
| phodal/harness-engineering | https://github.com/phodal/harness-engineering | 7 | Harness Engineering 개념 문서 (같은 저자의 entrix와 별도) | 개념 문서. entrix가 실제 도구 |
| charlesanim/harness-engineering | https://github.com/charlesanim/harness-engineering | 9 | OpenAI 하네스 엔지니어링 방법론 셋업 스킬 | 셋업 스킬(초기 설정만). 지속적 하네스 관리 없음 |
| adrielp/ai-engineering-harness | https://github.com/adrielp/ai-engineering-harness | 7 | 하네스 컨텍스트 엔지니어링 도구 | 컨텍스트 주입에 집중. 기계적 강제나 검증 없음 |
| ldzhouquan/agent-harness-skill | https://github.com/ldzhouquan/agent-harness-skill | 6 | Harness Engineering 체계적 구현 스킬 | 스킬 하나. 독립 도구가 아님 |
| ArtemisAI/Harness_Engineering | https://github.com/ArtemisAI/Harness_Engineering | 5 | 하네스 엔지니어링 템플릿 프로젝트 | 템플릿. 고유 기능 없음 |
| az9713/harness-engineering-blueprint | https://github.com/az9713/harness-engineering-blueprint | 4 | 하네스 엔지니어링 종합 가이드 | 가이드/문서. 도구가 아님 |
| Troyanovsky/simple-harness | https://github.com/Troyanovsky/simple-harness | 4 | 스펙 주도 에이전틱 개발용 심플 하네스 | 최소 구현. 차별점 부족 |
| SaltAdamW/Awesome-Harness-Engineering | https://github.com/SaltAdamW/Awesome-Harness-Engineering | 3 | Harness Engineering for Agents awesome list | awesome list |
| toy-crane/harness-engineering-template | https://github.com/toy-crane/harness-engineering-template | 20 | 하네스 엔지니어링 템플릿 | 템플릿. 설명 없음 |
| Dowwie/tasker | https://github.com/Dowwie/tasker | 18 | 스펙 주도 계획/실행 에이전틱 개발 프레임워크 (Go) | 스펙 주도 프레임워크이나 하네스 엔지니어링 관점 부족 |
| nightshiftco/nightshift | https://github.com/nightshiftco/nightshift | 26 | 오픈소스 하네스 엔지니어링 플랫폼. SSH 가능한 격리 머신(chicklet) 프로비저닝 | 런타임 격리 플랫폼. 하네스 엔지니어링 도구보다는 인프라에 가까움 |
| zhoushaw/Context-Engineering-to-Harness-Engin | https://github.com/zhoushaw/Context-Engineering-to-Harness-Engin | 47 | 컨텍스트 엔지니어링에서 하네스 엔지니어링까지 | 설명/README 없음 |
| MattMagg/agent-harness | https://github.com/MattMagg/agent-harness | 9 | 에이전트 하네스 문서 (원칙, 체크리스트, 불변식, 거버넌스) | 문서/가이드. 도구가 아님 |
| Intense-Visions/harness-engineering | https://github.com/Intense-Visions/harness-engineering | 3 | AI 에이전트를 위한 기계적 제약 | 소규모 템플릿. 차별점 부족 |
| usamadar/coding-agent-benchmark | https://github.com/usamadar/coding-agent-benchmark | 3 | 코딩 에이전트 벤치마크 하네스 | 벤치마크 특화. 개발용 하네스가 아님 |
