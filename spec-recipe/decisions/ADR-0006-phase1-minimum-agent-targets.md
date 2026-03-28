# ADR-0006: Phase 1 최소 Agent 타겟 범위

> **ID**: ADR-0006
> **Status**: Accepted
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: v0.9.0 build.py 확장

## 1. 맥락 및 문제 정의

build.py가 constraint를 agent별 규칙 파일로 변환한다. Phase 1에서 모든 타겟(Codex AGENTS.md, Cursor .cursor/rules, Kiro .kiro/steering, Claude Code CLAUDE.md)을 지원하면 개발 범위가 커진다. 최소 몇 개 타겟으로 시작하여 "동일 소스, 다른 출력" 구조를 검증해야 한다.

## 2. 고려된 대안

### 2.1 대안 1: AGENTS.md만
- **Pros**: 최소 범위, 빠른 구현
- **Cons**: "다른 출력" 검증 불가, Codex 전용이 됨

### 2.2 대안 2: AGENTS.md + CLAUDE.md
- **Pros**: 2개 타겟으로 "동일 소스, 다른 형식" 검증 가능, 둘 다 마크다운이라 구현 유사
- **Cons**: Cursor, Kiro 미지원

### 2.3 대안 3: AGENTS.md + CLAUDE.md + .cursor/rules/
- **Pros**: 3대 주요 agent 커버
- **Cons**: .cursor/rules/는 디렉토리 기반이라 구현 패턴이 다름, Phase 1 범위 초과

## 3. 결정

**대안 2: AGENTS.md + CLAUDE.md**를 선택한다.

### 3.1 결정의 근거

1. 두 형식 모두 단일 마크다운 파일이므로 변환 로직이 유사하고 구현 비용이 낮다.
2. 두 형식의 차이점(섹션 구조, 헤더 스타일)을 통해 "동일 코어, 다른 렌더링" 아키텍처를 검증할 수 있다.
3. AGENTS.md는 Codex 표준, CLAUDE.md는 Claude Code 표준으로, 가장 활발한 2개 agent를 커버한다.
4. Phase 2 이후 .cursor/rules(디렉토리 기반), .kiro/steering(디렉토리 기반)을 추가하면 파일 기반 → 디렉토리 기반 확장을 점진적으로 테스트할 수 있다.

### 3.2 타겟별 변환 규칙 (Phase 1)

| 소스 | AGENTS.md (Codex) | CLAUDE.md (Claude Code) |
|------|-------------------|------------------------|
| invariants/ | `## Absolute Rules` 섹션 | `## Security Rules` 섹션 |
| principles/ | `## Development Principles` 섹션 | `## Principles` 섹션 |
| conventions/ | `## Conventions` 섹션 | `## Conventions` 섹션 |
| feedback (미해결) | 파일 상단 `## PENDING VIOLATIONS` | 파일 상단 `## PENDING VIOLATIONS` |

## 4. 영향

- **Positive**: 최소 비용으로 아키텍처 검증, 2대 주요 agent 커버
- **Negative**: Cursor, Kiro 사용자는 Phase 2까지 대기
- **Follow-up**:
  - Phase 2에서 .cursor/rules, .kiro/steering 추가
  - 타겟 추가 시 변환 인터페이스 표준화 (타겟 어댑터 패턴)
