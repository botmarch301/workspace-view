# ADR-0008: Recipe / Kitchen 용어 정의

> **ID**: ADR-0008
> **Status**: Accepted
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: 전체 문서, glossary.md

## 1. 맥락 및 문제 정의

spec-recipe 프레임워크를 개발하면서 동시에 그 프레임워크를 사용하여 SDD를 수행하는 도그푸딩 방식으로 진행하고 있다. 이 과정에서 "프레임워크 자체에 대한 작업"과 "프레임워크의 산출물을 사용하는 작업"이 구분 없이 혼재되어 있다.

예시:
- ADR은 Recipe 개발 과정의 의사결정이면서, Kitchen에서도 사용 가능한 프로세스다
- "기계적 검증 vs AI 검증" 분리는 Kitchen(사용자 프로젝트)에서의 요구사항이다
- constraint invariant 7개는 Recipe에서 정의하고 Kitchen에 제공되는 것이다
- Phase Separation 원칙은 Recipe와 Kitchen 양쪽에 적용된다

이 모호함을 해소하기 위해 용어를 정의한다.

## 2. 결정

### 2.1 Recipe

**spec-recipe 프레임워크 자체.** 코어 원칙, 검증 기준, 빌드 시스템, 스키마 정의, 스크립트, 타겟 빌드 설정 등을 포함한다.

"요리법을 만드는 작업."

- 코어 원칙 정의 (principles.md)
- 검증 항목/기준 정의 (verification.md)
- 제약 스키마 정의 (constraint YAML 형식)
- 빌드 시스템 (build.py, 타겟 매핑)
- 프로세스 정의 (processes.md)
- 스크립트 구현 (verify-*.py, init.py, pre-commit)

### 2.2 Kitchen

**Recipe에서 빌드된 산출물이 설치되어, 사용자가 실제로 SDD를 수행하는 환경.** 사용자의 프로젝트에 적용된 상태.

"요리법을 가지고 실제로 요리하는 현장."

Kitchen의 형태:

| 형태 | 설명 | 예시 |
|------|------|------|
| spec-kit 프리셋 | Spec Kit 생태계에서 작동 | `specify init --preset spec-recipe` |
| BMAD 모듈 | BMAD 생태계에서 작동 | `npx bmad-method install --modules spec-recipe` |
| 독립형 (standalone) | 타겟 없이 코어만으로 작동 | `spec-recipe init .` |
| Kiro steering | Kiro IDE에서 작동 | `.kiro/steering/` 파일 세트 |
| Claude Code | CLAUDE.md 기반 | `CLAUDE.md` + `.spec-recipe/` |

### 2.3 적용 범위 분류

모든 요구사항, 원칙, 기능은 다음 중 하나로 분류한다:

| 분류 | 의미 | 예시 |
|------|------|------|
| **Recipe-only** | 프레임워크 개발에만 적용 | build.py 내부 구현, 타겟 빌드 로직 |
| **Kitchen-only** | 사용자 프로젝트에만 적용 | 기계적 검증 실행, 기본 invariant 7개, pre-commit 동작 |
| **Universal** | Recipe와 Kitchen 양쪽에 적용 | 코어 원칙(Phase Separation 등), ADR 프로세스, 이슈 추적 |

## 3. 근거

1. 도그푸딩으로 인한 모호함을 제거한다
2. "이 기능은 누구를 위한 것인가"를 명확히 하여 설계/구현의 방향을 잡는다
3. spec-recipe의 비유(레시피/요리)를 자연스럽게 활용한다

## 4. 영향

- **Positive**: 요구사항의 대상이 명확해짐, 문서의 독자가 명확해짐
- **Follow-up**:
  - glossary.md에 Recipe, Kitchen 용어 추가
  - 기존 ADR, 설계안, 리서치 문서에서 모호한 부분 분류 태그 추가
  - 향후 모든 요구사항/기능에 [Recipe-only], [Kitchen-only], [Universal] 태그 부여
