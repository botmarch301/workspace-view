# ADR-0004: Agent 규칙 파일 자동 재생성 트리거 방식

> **ID**: ADR-0004
> **Status**: Accepted
> **Date**: 2026-03-28
> **Deciders**: Mingi
> **Implies**: v0.9.0 Agent 주입 파이프라인

## 1. 맥락 및 문제 정의

build.py가 constraint YAML을 AGENTS.md, CLAUDE.md 등으로 변환한다. constraint를 수정하면 agent 규칙 파일도 갱신되어야 하는데, 이 갱신이 어떤 시점에 어떻게 발생하는지 정의해야 한다.

constraint를 수정했는데 agent 규칙 파일을 재생성하지 않으면:
- agent가 구버전 규칙으로 작업
- constraint ↔ agent 규칙 파일 사이에 drift 발생
- 가장 위험한 시나리오: invariant를 추가했는데 AGENTS.md에 반영 안 됨

## 2. 고려된 대안

### 2.1 대안 1: constraint 저장 시 자동 실행 (Watcher)
constraint 파일 변경을 감시하여 즉시 agent 규칙 파일을 재생성한다.
- **Pros**: 항상 동기화 보장, 사용자 개입 불필요
- **Cons**: 의도치 않은 파일 변경 발생 (편집 중에도 재생성), Watcher 의존

### 2.2 대안 2: pre-commit에서 검사만 (불일치 시 차단)
커밋 시 constraint의 해시와 agent 규칙 파일에 기록된 해시를 비교. 불일치 시 커밋 차단 + "spec-recipe build 실행 필요" 메시지.
- **Pros**: 명시적 빌드 단계, 의도치 않은 변경 없음
- **Cons**: 사용자가 build 명령을 수동 실행해야 함

### 2.3 대안 3: pre-commit에서 검사 + 자동 재생성
불일치 감지 시 자동으로 재생성하고 커밋에 포함한다.
- **Pros**: 사용자 부담 최소
- **Cons**: pre-commit에서 파일 수정은 예상치 못한 동작, git staging 영역 변경

## 3. 결정

**대안 2: pre-commit에서 검사만 (불일치 시 차단)**을 선택한다.

### 3.1 결정의 근거

1. agent 규칙 파일은 **빌드 산출물**이다. 빌드는 명시적 단계여야 한다.
2. pre-commit에서 자동으로 파일을 수정/생성하면 git staging 영역이 변하여 사용자가 혼란스러워할 수 있다.
3. `spec-recipe build` 명령을 실행하는 것은 단순하고 예측 가능하다.
4. constraint 수정 빈도는 높지 않으므로 수동 빌드 부담이 크지 않다.

### 3.2 동기화 검사 구현

```python
# pre-commit hook 내부
def check_agent_rule_sync():
    constraint_hash = compute_hash("constraints/")
    for rule_file in ["AGENTS.md", "CLAUDE.md"]:
        embedded_hash = extract_hash(rule_file)  # 파일 상단 주석에서 추출
        if constraint_hash != embedded_hash:
            fail(f"{rule_file}이 constraint와 동기화되지 않았습니다. "
                 f"'spec-recipe build'를 실행해주세요.")
```

agent 규칙 파일 상단:
```markdown
<!-- spec-recipe:constraint-hash:a1b2c3d4 -->
<!-- 이 파일은 자동 생성됩니다. 수동 수정하지 마세요. -->
<!-- 재생성: spec-recipe build -->
```

## 4. 영향

- **Positive**: 명시적 빌드 단계로 예측 가능, drift 기계적 감지
- **Negative**: 사용자가 build를 잊으면 커밋 차단 → 약간의 마찰
- **Follow-up**:
  - build.py에 constraint 해시 계산 + 규칙 파일 상단 삽입 로직 추가
  - pre-commit hook에 해시 비교 체크 추가
  - 이슈 레지스트리에 "constraint ↔ agent 규칙 불일치" 자동 등록
