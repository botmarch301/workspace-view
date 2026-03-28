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

### 대중화 도구 (5개)

| # | 이름 | URL | Stars | 요약 | 선별 이유 |
|---|------|-----|-------|------|----------|
| 1 | harness-engineering-playbook | https://github.com/lipingtababa/harness-engineering-playbook | 42 | 팀 환경에서 AI agent와 품질 소프트웨어를 출하하기 위한 실전 프레임워크. 결정론적 smoke/test/lint 하네스 커맨드와 아키텍처 경계 강제. | OpenAI 하네스 엔지니어링 원칙을 가장 체계적으로 Playbook 형태로 정리. 팀 환경 고려가 독특. |
| 2 | entrix | https://github.com/phodal/entrix | 31 | 품질 규칙, 아키텍처 제약, 검증 단계를 실행 가능한 가드레일로 변환하는 하네스 엔지니어링 도구. CLI + Claude Code 플러그인. | 유일하게 "규칙을 실행 가능한 가드레일로 변환"하는 도구. tier별 검증(fast/normal/deep), 변경 인식 검증, 리뷰 트리거 등 기계적 강제 메커니즘 보유. |
| 3 | deepklarity/harness-kit | https://github.com/deepklarity/harness-kit | 29 | AI agent와의 작업을 위한 키트. 오케스트레이션뿐 아니라 그 주변의 엔지니어링 패턴까지 포함. TDD 우선 실행, 구조화된 디버깅, 지식 축적, 비용 인식 위임. | 칸반 보드 + DAG 기반 태스크 분해 + 다중 agent 실행을 시각적으로 제공. "각 실행이 다음 실행을 개선한다"는 복합 성장 패턴. |
| 4 | andrew-yangy/gru-ai | https://github.com/andrew-yangy/gru-ai | 108 | 1인 회사를 위한 자율 AI 에이전트 팀. 컨텍스트 엔지니어링 + 하네스 엔지니어링으로 브레인스토밍부터 배포까지 파이프라인 구동. | "CEO처럼 지시하면 agent 팀이 실행" 패턴. 엔지니어링 외에 마케팅/운영까지 포괄하는 멀티 에이전트 오케스트레이션. 컨텍스트 트리 기반 지식 축적. |
| 5 | jrenaldi79/harness-engineering | https://github.com/jrenaldi79/harness-engineering | 47 | 코딩 에이전트를 위한 컨텍스트 엔지니어링. CLAUDE.md 템플릿, 기계적 강제(git hooks, pre-commit), 20+ 베스트 프랙티스 필드 가이드. | "agent는 지시를 듣지 않는다"는 전제에서 출발. git hooks, pre-commit으로 기계적 강제를 구현하는 실전적 접근. Andrej Karpathy 인용이 핵심 동기. |

### 주시 도구 (3개)

| # | 이름 | URL | Stars | 요약 | 선별 이유 |
|---|------|-----|-------|------|----------|
| 6 | markmishaev76/ai-harness-scorecard | https://github.com/markmishaev76/ai-harness-scorecard | 14 | 리포지토리의 엔지니어링 세이프가드를 등급화하는 평가 도구. DORA 2025, OpenAI Harness Engineering, SlopCodeBench, Kent Beck 기반. | "agent가 여기서 만들 코드가 신뢰 가능한가?"라는 독특한 관점. 5개 카테고리 31개 체크로 정량 평가. 기존 도구가 "만드는 것"에 집중할 때 유일하게 "측정"에 집중. |
| 7 | WellDunDun/reins | https://github.com/WellDunDun/reins | 6 | Harness Engineering CLI. scaffold, audit, evolve, doctor로 리포의 agent 준비도를 관리. OpenAI 방법론의 도구화. | "OpenAI가 방법론을 발표했고, 우리는 도구를 만들었다"는 명확한 포지셔닝. scaffold → audit → evolve → doctor 4단계 CLI로 하네스 성숙도를 점진적으로 높이는 접근. 의존성 0개. |
| 8 | SuperagenticAI/superqode | https://github.com/SuperagenticAI/superqode | 7 | Agent-Native 코딩 하네스. 품질 중심 에이전틱 소프트웨어 개발. "agent가 코드를 깨뜨리게 놔두고, 수정을 증명하고, 확신을 갖고 출하한다." | "깨뜨리기 → 증명하기 → 출하하기" 패턴이 독특. 품질 엔지니어링 관점에서 하네스를 접근하는 유일한 도구. |

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
