# ADR-0005: Metrics 데이터의 Git 추적 여부

> **ID**: ADR-0005
> **Status**: Accepted
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: v0.9.0 측정 내장 (metrics/)

## 1. 맥락 및 문제 정의

`.spec-recipe/metrics/`에 검증 결과를 누적한다. 이 데이터를 git에 포함할지 .gitignore에 넣을지 결정해야 한다.

metrics 데이터의 특성:
- 매 커밋마다 JSON 파일이 추가됨 (runs/ 디렉토리)
- summary.json이 현재 상태를 요약
- 시간이 지나면 데이터가 상당히 쌓일 수 있음

## 2. 고려된 대안

### 2.1 대안 1: Git 추적
- **Pros**: 팀 공유 가능, 추이 보존, 브랜치별 비교 가능, CI에서 접근 가능
- **Cons**: 리포 크기 증가, 커밋 히스토리에 노이즈

### 2.2 대안 2: .gitignore
- **Pros**: 리포 깨끗, 커밋 히스토리 오염 없음
- **Cons**: 팀 공유 불가, 로컬에서만 보임, CI에서 이전 데이터 접근 불가

### 2.3 대안 3: summary.json만 추적, runs/는 .gitignore
- **Pros**: 핵심 상태는 공유, 상세 이력은 로컬 보관으로 리포 크기 관리
- **Cons**: 상세 추이 분석 시 로컬 데이터 필요

## 3. 결정

**대안 3: summary.json만 추적, runs/는 .gitignore**를 선택한다.

### 3.1 결정의 근거

1. summary.json은 현재 하네스 수준의 스냅샷이다. 팀원/CI가 알아야 하는 정보.
2. runs/의 개별 실행 기록은 상세 분석 시에만 필요하며, 매 커밋마다 쌓이면 리포 크기가 무한히 증가한다.
3. milestone 리포트 생성 시 runs/ 데이터를 사용하지만, 리포트 자체는 별도 파일로 git 추적하면 된다.
4. CI 환경에서는 해당 빌드의 runs/ 데이터만 있으면 충분하다 (이전 빌드와의 비교는 summary.json으로).

### 3.2 구조

```
.spec-recipe/
  metrics/
    summary.json        # git 추적 O — 현재 상태 스냅샷
    runs/               # git 추적 X — 상세 실행 기록
      .gitkeep
    reports/            # git 추적 O — milestone 리포트
```

```gitignore
# .spec-recipe/metrics/ 부분 추적
.spec-recipe/metrics/runs/*
!.spec-recipe/metrics/runs/.gitkeep
```

## 4. 영향

- **Positive**: 핵심 지표 공유 + 리포 크기 관리 균형
- **Negative**: 로컬 runs/ 데이터 손실 시 상세 추이 분석 제한
- **Follow-up**:
  - init.py에 metrics/ 구조 + .gitignore 생성 추가
  - summary.json 스키마 정의
  - milestone 리포트 생성 시 runs/ → reports/ 변환 로직
