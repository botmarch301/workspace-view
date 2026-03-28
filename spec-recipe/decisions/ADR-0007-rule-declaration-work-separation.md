# ADR-0007: 룰 선언 작업과 개발/테스트 작업의 분리 원칙

> **ID**: ADR-0007
> **Status**: Accepted
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: CORE-PRC-001, CORE-PRC-002, v0.9.0 전체 프로세스

## 1. 맥락 및 문제 정의

ADR-0003에서 "예외는 룰 레벨에서 관리하며, 개발 중에 임의로 만들 수 없다"는 원칙이 도출되었다. 이 원칙은 예외뿐 아니라 spec-recipe의 전체 프로세스에 적용되어야 할 상위 원칙이다.

스펙과 룰을 선언하는 작업과, 설계/개발/테스트 작업이 혼재되면:
1. 개발 중 불편한 룰을 즉석에서 수정하거나 약화시킬 수 있다
2. 제약의 변경 이력이 개발 커밋에 묻혀 추적이 어렵다
3. 검증자(또는 검증 스크립트)가 참조하는 룰이 작업 중에 바뀌면 검증 기준 자체가 흔들린다
4. "구현 주체 ≠ 검증 주체" 원칙(Verification Separation)의 확장

## 2. 결정

**스펙/룰/제약의 선언과 설계/개발/테스트의 실행은 반드시 분리한다.**

### 2.1 분리 대상: 4개 작업 영역

| 선언 작업 (Specification) | 설계 작업 (Design) | 개발 작업 (Development) | 테스트 작업 (Testing) |
|--------------------------|-------------------|----------------------|---------------------|
| 요구사항 문서 작성/수정 | 아키텍처 설계 | 소스 코드 작성/수정 | 테스트 코드 작성/수정 |
| constraint 정의/수정 | API/스키마 설계 | 리팩토링 | 테스트 실행/결과 분석 |
| 예외 등록/수정 | 설계 문서 작성/수정 | 설정 파일 수정 | 커버리지 분석 |
| ADR 작성 | 기술 선택/결정 | 빌드/배포 | 뮤테이션 테스트 |
| build (agent 규칙 생성) | | | |

**4자 분리 원칙:**
- 선언(Specification)과 설계(Design)의 분리 → 설계 편의에 맞춰 요구사항을 왜곡하는 것 차단
- 설계(Design)와 개발(Development)의 분리 → 구현 편의에 맞춰 설계를 임의 변경하는 것 차단
- 개발(Development)과 테스트(Testing)의 분리 → 구현자가 자기 코드에 맞춰 테스트를 왜곡하는 것 차단
- 선언(Specification)과 테스트(Testing)의 분리 → 테스트 결과에 맞춰 스펙/룰을 후행 수정하는 것 차단
- 선언(Specification)과 개발(Development)의 분리 → 개발 중 룰 임의 변경 차단
- 설계(Design)와 테스트(Testing)의 분리 → 테스트 실패를 이유로 설계를 무단 변경하는 것 차단

이것은 기존 원칙 7(Verification Separation: 구현 주체 ≠ 검증 주체)의 확장이다. Verification Separation이 "누가"의 분리라면, 이 원칙은 "언제/무엇을"의 분리다. 소프트웨어 공학의 V-Model에서 각 단계가 독립적으로 수행되어야 하는 것과 같은 원리다.

### 2.2 강제 메커니즘

1. **커밋 분리**: 3개 경로 그룹의 동시 변경을 금지한다. pre-commit에서 차단.

   ```
   # 4개 경로 그룹 — 같은 커밋에 2개 이상 그룹의 변경이 포함되면 차단
   specification_paths: [".spec-recipe/constraints/", "spec/0-context/", "spec/1-requirements/", "decisions/"]
   design_paths:        ["spec/2-design/", "spec/3-plan/"]
   development_paths:   ["src/", "lib/", "app/", "config/"]
   testing_paths:       ["tests/", "test/", "**/*_test.*", "**/*_spec.*"]
   ```

   동일 커밋에 2개 이상 그룹의 파일이 포함되면 차단. 각 영역의 작업은 독립된 커밋으로 수행한다.

2. **세션 분리 권고**: AI agent 환경에서는 선언 세션, 설계 세션, 개발 세션, 테스트 세션을 분리하는 것을 권고한다. 동일 세션에서 수행하더라도 커밋 분리는 강제된다.

3. **Phase Gate 확인**: 각 phase gate에서 "직전 단계에서 어떤 작업 영역의 변경이 있었는가? 커밋이 영역별로 분리되었는가?" 확인.

### 2.3 Agent 롤 분리 (빌드 타겟 가이드)

커밋 분리는 코어에서 기계적으로 강제한다. Agent 롤(역할) 분리는 agent 런타임에 따라 방법이 다르므로, 코어에서는 강제하지 않고 빌드 타겟별 가이드로 제공한다.

| 타겟 | 롤 분리 방법 |
|------|-------------|
| BMAD | 전문 페르소나(PM, Architect, Developer, Tester)로 분리 |
| Codex | 디렉토리별 AGENTS.md로 작업 범위 제한 |
| Kiro | agent 정의의 tools/allowedTools로 접근 가능 파일 제한 |
| Cursor | .cursor/rules/ 내 Auto 규칙으로 파일 패턴별 지시 분리 |

상세는 각 타겟의 빌드 가이드에서 기술한다.

### 2.4 예외

- **init 단계**: `spec-recipe init`은 constraint + 프로젝트 구조를 동시에 생성하므로 예외. 최초 설정은 하나의 커밋으로 허용.
- **문서 전용 변경**: README, CHANGELOG 등 비규칙/비코드 문서는 어느 쪽과도 동시 커밋 가능.

## 3. 근거

1. **"구현 주체 ≠ 검증 주체"의 확장**: 검증 기준(룰)을 정하는 사람과 검증 대상(코드)을 만드는 사람이 같은 작업에서 행동하면 이해충돌이 발생한다.
2. **변경 이력의 명확성**: 룰 변경과 코드 변경이 분리되면 git log에서 "언제 어떤 룰이 바뀌었고, 그 후 코드가 어떻게 바뀌었는지" 추적이 가능하다.
3. **AI agent 환경에서의 필수성**: agent가 개발 중에 "이 constraint가 불편하니 수정하자"라고 판단하는 것을 구조적으로 차단.

## 4. 영향

- **Positive**: 룰의 안정성 보장, 변경 이력 명확, agent의 룰 임의 조작 차단
- **Negative**: 커밋 분리 마찰 (하지만 품질 보장에 필수적인 비용)
- **Follow-up**:
  - pre-commit hook에 4개 경로 그룹 동시 변경 차단 로직 추가
  - processes.md에 "작업 분리 원칙" 섹션 추가
  - principles.md에 8번째 원칙으로 "Phase Separation" 추가 (Specification / Design / Development / Testing)
  - 기존 원칙 7(Verification Separation)과의 관계 명시: 7은 "주체 분리", 8은 "작업 분리"
