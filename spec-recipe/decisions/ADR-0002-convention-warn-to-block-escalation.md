# ADR-0002: Convention WARN → BLOCK 승격 임계값

> **ID**: ADR-0002
> **Status**: Proposed
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: v0.9.0 제약 체계 (constraints/)

## 1. 맥락 및 문제 정의

3계층 제약 모델(Invariant/Principle/Convention)에서 Convention 위반은 WARN으로 처리되어 커밋이 허용된다. 그러나 동일한 Convention 위반이 반복되면, 그것은 "무시되는 규칙"이 되어 Convention 체계 자체의 신뢰를 떨어뜨린다.

반복된 WARN을 방치하면:
1. agent가 "WARN은 무시해도 된다"는 패턴을 학습
2. Convention이 사실상 무력화
3. 코드베이스 품질이 점진적으로 하락

반면 너무 빨리 BLOCK으로 승격하면:
1. 소규모 프로젝트에서 과도한 제약
2. 리팩토링 중간 단계에서 불필요한 차단
3. 개발 속도 저하

## 2. 고려된 대안

### 2.1 대안 1: 고정 임계값 3회
- **Pros**: 단순, 예측 가능
- **Cons**: 프로젝트 규모/성격에 무관하게 일률 적용

### 2.2 대안 2: 고정 임계값 5회
- **Pros**: 더 관대, 리팩토링 여유
- **Cons**: 5회 반복이면 이미 습관화된 위반

### 2.3 대안 3: 사용자 설정 가능, 기본값 3회
- **Pros**: 프로젝트별 맞춤, maturity profile과 연동 가능
- **Cons**: 설정 항목 하나 더 추가

## 3. 결정

**대안 3: 사용자 설정 가능, 기본값 3회**를 선택한다.

### 3.1 결정의 근거

1. spec-recipe의 maturity profile(basic/intermediate/advanced)에 따라 다른 기본값을 제공하면 점진적 도입이 자연스럽다
   - basic: 5회 (관대)
   - intermediate: 3회 (기본)
   - advanced: 2회 (엄격)
2. 사용자가 개별 Convention별로 임계값을 재정의할 수 있으면 유연성 확보
3. 승격 시 feedback에 "WARN→BLOCK 승격 사유: 동일 위반 N회 반복" 기록으로 투명성 확보

### 3.2 설정 형식

```yaml
# .spec-recipe/verification-config.yml
convention_escalation:
  default_threshold: 3        # 기본 임계값
  per_convention:              # 개별 재정의 (선택)
    CONV-STYLE-001: 5          # 이 컨벤션은 5회까지 허용
  reset_on: "milestone"        # 카운터 리셋 시점: milestone | sprint | never
```

## 4. 영향

- **Positive**: Convention 체계의 실효성 유지, 프로젝트별 맞춤 가능
- **Negative**: 설정 복잡도 약간 증가
- **Follow-up**: constraint YAML 스키마에 escalation 필드 추가, metrics에 승격 이력 추적
