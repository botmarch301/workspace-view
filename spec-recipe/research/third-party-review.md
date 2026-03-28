# spec-recipe 개선 방향 제3자 검토서

> 작성일: 2026-03-28
> 검토 기준: ISO/IEC 12207 프로세스 커버리지 + CMMI 성숙도 모델
> 검토 대상: spec-recipe v0.8.0 (현재) + v0.9.0 설계안 (제약 주입 + 피드백 루프)
> 참고 자료: harness-engineering-landscape.md, design-constraint-injection-feedback-loop.md, 블로그 2편 분석 프레임

---

## 1. 현재 spec-recipe의 위치 평가

### 1.1 ISO 12207 프로세스 커버리지

| 프로세스 | 커버 여부 | 근거 |
|----------|----------|------|
| 요구사항 정의 | **O** | principles.md의 Spec-First, processes.md의 Spec Creation |
| 설계 | **O** | SoC 원칙, structure.md의 디렉토리 계층 |
| 구현 | **O** | processes.md의 Code Synchronization, Forward Sync |
| 검증(V&V) | **O** | verification.md 25+개 기계적 체크, 3-way Contract |
| 품질 보증 | **triangle** | 정적 분석 기준 정의됨 (V-STA), 하지만 강제 메커니즘이 pre-commit에 한정 |
| 측정/분석 | **X** | 커버리지 비율, 복잡도 임계값 정의는 있으나 하네스 수준 자체의 정량 측정 없음 |
| 구성 관리 | **triangle** | Drift Detection이 코드-스펙 동기화를 다루나, 변경 이력 추적/베이스라인 관리는 git 의존 |

**진단**: spec-recipe는 요구사항~검증까지의 전반부 프로세스를 잘 커버한다. 다만 "검증 결과를 기반으로 프로세스를 개선하는" 후반부(측정/분석, 지속적 개선)가 비어 있다. 이는 경쟁 도구 대부분과 공통된 한계이지만, spec-recipe가 "메타 프레임워크"를 표방한다면 이 영역까지 다뤄야 한다.

### 1.2 CMMI 성숙도 평가

**현재 수준: Level 3 (Defined)**

| 레벨 | 상태 | 근거 |
|------|------|------|
| Level 1 (Initial) | 통과 | 프로세스가 명시적으로 정의됨 |
| Level 2 (Managed) | 통과 | 요구사항 관리, 프로젝트 계획, 검증 기준 존재 |
| Level 3 (Defined) | **현재 위치** | 프로세스가 조직 차원에서 문서화, 프로젝트 간 일관성(코어 원칙), 빌드 타겟 매핑 |
| Level 4 (Quantitatively Managed) | 미도달 | 프로세스의 정량적 측정/관리 부재 |
| Level 5 (Optimizing) | 미도달 | 측정 기반 지속적 개선 루프 부재 |

**비교 시사점**:
블로그 2편의 분석에서 Kiro가 Level 3, Entrix가 Level 3~4, Scorecard가 Level 4로 평가되었다. spec-recipe는 검증 체계의 정의 수준에서 Kiro와 동등하지만, Entrix의 "실행 가능한 가드레일"이나 Scorecard의 "정량 측정"에 해당하는 기능이 없다.

### 1.3 핵심 Gap 요약

| Gap | 현재 상태 | 영향 | 설계안 대응 여부 |
|-----|----------|------|----------------|
| **G1. 원칙의 agent 전달 부재** | principles.md는 인간 문서 | agent가 원칙을 모른 채 작업 | v0.9.0 A(제약 주입)에서 대응 |
| **G2. 계층적 제약 부재** | 모든 원칙이 동일 수준 | 보안 위반과 네이밍 위반의 경중 구분 불가 | v0.9.0 A(INV/PRC/CONV)에서 대응 |
| **G3. 피드백 루프 부재** | FAIL 감지만, agent 재주입 없음 | 인간이 수동으로 FAIL 전달 | v0.9.0 B(피드백 루프)에서 대응 |
| **G4. 정량 측정 부재** | 커버리지/복잡도 기준은 있으나 하네스 성숙도 측정 없음 | 개선 추적 불가 | v0.9.0 C(하네스 수준 측정)에서 대응 예정 |
| **G5. 지속적 개선 루프 부재** | 측정 → 개선의 자동 연결 없음 | Level 5 진입 불가 | 설계안에 아직 없음 |

---

## 2. 설계안(v0.9.0) 검토

### 2.1 제약 주입 (A) 검토

**강점**:
- 3계층 모델(Invariant/Principle/Convention)은 기존 도구에 없는 고유한 차별점이다. Spec Kit의 constitution은 단일 레벨, Kiro의 steering도 우선순위 구분이 없다.
- YAML + Markdown 하이브리드 형식은 AI-Rule-Spec의 방향과 일치하며, 기계 파싱과 인간 가독성을 모두 확보한다.
- 위반 시 대응(HALT/BLOCK/WARN)이 계층별로 명확하게 분리된 점은 실무적으로 유용하다.

**우려 사항**:

**(a) detection.method의 한계**

현재 설계안의 감지 방법이 regex, AST, script, tool 4가지인데, 대부분의 invariant 규칙이 regex 기반이다. regex로 감지 가능한 보안 위반은 "명백한 패턴"에 한정된다.

예를 들어 INV-SEC-001(하드코딩된 시크릿)의 regex 패턴 `password\s*=\s*["\'][^"\']{8,}`은 `password = "abc12345"`는 잡지만, 다음은 잡지 못한다:
```python
creds = {"pass": "abc12345"}       # 키 이름이 다름
pw = base64.b64decode("...")       # 인코딩됨
```

Entrix가 "tier별 검증(fast/normal/deep)"을 도입한 이유가 여기에 있다. fast tier는 regex, deep tier는 데이터 흐름 분석까지 수행한다.

**권고**: invariant 규칙에 `depth` 필드를 추가하여, 검증 깊이를 선택할 수 있도록 하는 것이 좋다. 파일 저장 시에는 fast(regex), 커밋 시에는 normal(AST), CI에서는 deep(외부 도구 연동).

**(b) agent 규칙 파일 생성의 동기화 문제**

build.py가 constraint YAML을 AGENTS.md/CLAUDE.md 등으로 변환하는데, 이 변환이 언제 실행되는가? constraint를 수정할 때마다 수동으로 build를 실행해야 한다면, constraint와 agent 규칙 파일 사이에 drift가 발생한다.

**권고**: constraint 변경 시 agent 규칙 파일을 자동 재생성하는 hook을 추가. 또는 agent 규칙 파일에 "이 파일은 자동 생성됨, 수동 수정 금지" 경고와 함께 소스 constraint의 해시를 포함하여, 불일치를 pre-commit에서 감지.

**(c) Convention의 정의 범위**

설계안에서 convention은 "사용자 정의, 프로젝트별"로 기술되어 있는데, 빈 디렉토리 + 템플릿만 제공한다면 실제로 convention을 작성하는 사용자는 소수일 것이다.

Agent OS의 `/discover-standards` 방식이 참고할 만하다 -- 기존 코드베이스를 분석하여 패턴을 자동 추출하고 convention으로 문서화하는 접근.

**권고**: `spec-recipe discover-conventions` 명령어를 추가하여, 기존 코드에서 네이밍 패턴, 디렉토리 구조, import 규칙 등을 자동 추출 → convention YAML 초안 생성.

### 2.2 피드백 루프 (B) 검토

**강점**:
- feedback/current.md를 통한 agent 독립적 피드백 채널은 현존 도구 중 유일한 접근이다. Kiro Hooks는 IDE 종속이고, OpenAI의 agent-to-agent 리뷰는 Codex 종속이다.
- HALT/BLOCK/WARN의 단계별 대응이 교정 사이클(processes.md의 P1/P2/P3)과 자연스럽게 연결된다.

**우려 사항**:

**(a) feedback/current.md의 agent 준수 보장**

설계안의 핵심 가정은 "agent가 작업 전 feedback/current.md를 확인한다"인데, 이것은 agent 규칙 파일에 "확인하세요"라고 쓰는 것에 의존한다. 이것은 **가이드라인이지 게이트가 아니다**.

agent가 feedback을 무시하고 작업을 진행해도, pre-commit 시점까지는 차단되지 않는다.

**권고**: 두 가지 보완 경로.
1. **기계적 게이트 강화**: pre-commit에서 "HALT 미해결 상태에서의 모든 커밋 차단"은 이미 설계에 있다. 이것이 최종 방어선.
2. **피드백 주입 강화**: agent 규칙 파일 자체에 feedback 내용을 직접 포함시키는 방식. 매번 규칙 파일을 재생성할 때 미해결 HALT/BLOCK 항목을 규칙 파일 상단에 인라인하면, agent가 별도 파일을 "확인하는" 행동에 의존하지 않아도 된다.

**(b) 피드백 루프의 종료 조건**

agent가 교정을 시도했으나 계속 FAIL하는 경우의 처리가 정의되어 있지 않다. 무한 루프에 빠질 수 있다.

**권고**: 교정 시도 횟수 상한을 설정하고, 상한 초과 시 "인간 개입 요청(ESCALATE)" 상태로 전환. feedback/current.md에 `attempts: 3/3, status: ESCALATE` 형태로 기록.

**(c) 실시간 Watcher의 실효성**

설계안의 Phase 3(fswatch/inotify 기반 실시간 감시)는 선택적으로 되어 있다. 그런데 agent가 작업하는 동안 파일 저장이 빈번하게 발생하면 watcher가 검증을 과도하게 실행할 수 있다.

**권고**: debounce 메커니즘 필수 (마지막 변경 후 N초 대기). 그리고 watcher는 invariant(보안) 검증만 실행하고, 나머지는 커밋 시점으로 한정. 이 구분은 설계안에 이미 있으나 명시적 debounce가 빠져 있다.

### 2.3 미포함 영역: 측정(C)과 지속적 개선

설계안은 A+B에 집중하고 C(측정)는 별도로 진행한다고 되어 있다. 하지만 **A+B+C가 연결되어야** spec-recipe의 진정한 차별점이 완성된다.

블로그 2편에서 지적한 핵심:

> "Level 5(Optimizing) — 측정 결과를 기반으로 프로세스가 지속 개선되는 단계 — 에 도달한 도구는 없다. 측정(Scorecard)과 개선(Reins의 evolve)을 각각 다루는 도구는 있지만, 이 둘이 자동으로 연결되어 지속적 개선 루프를 형성하는 도구는 아직 존재하지 않는다."

이것이 spec-recipe가 노릴 수 있는 빈자리다.

**제안: C를 A+B와 분리하지 말고, 측정의 최소 단위를 A+B에 내장시키는 것을 권고.**

구체적으로:
- 매 커밋 시 검증 실행 → 결과를 `.spec-recipe/metrics/` 에 누적
- 추적 지표: invariant 위반 건수 추이, principle 준수율 추이, convention 준수율 추이, 교정 소요 시간, 교정 시도 횟수
- 주기적 리포트 자동 생성 (예: milestone 종료 시)
- 리포트에서 반복 패턴 → 새로운 constraint 제안 또는 기존 constraint 조정

이렇게 하면 A+B+C가 하나의 루프로 연결된다:

```
제약 정의(A) → 검증+피드백(B) → 측정(C) → 제약 조정(A) → ...
```

이것이 CMMI Level 5(Optimizing)의 구조다.

---

## 3. 경쟁 도구 대비 차별점 재평가

블로그 2편의 비교 프레임으로 spec-recipe v0.9.0(설계안 반영 후)을 재평가한다.

### 3.1 ISO 12207 프로세스 커버리지 (설계안 반영 후)

| 프로세스 | v0.8.0 | v0.9.0 (설계안) | 비고 |
|----------|--------|----------------|------|
| 요구사항 정의 | O | O | 변화 없음 |
| 설계 | O | O | 변화 없음 |
| 구현 | O | O | 변화 없음 |
| 검증(V&V) | O | **O+** | 피드백 루프 추가로 검증 실효성 강화 |
| 품질 보증 | triangle | **O** | 제약 주입 + 기계적 강제로 품질 보증 체계 완성 |
| 측정/분석 | X | **triangle~O** | C를 내장하면 O, 분리하면 triangle |
| 구성 관리 | triangle | triangle | 변화 없음 (git 의존) |

### 3.2 CMMI 성숙도 (설계안 반영 후)

| 시나리오 | 목표 성숙도 | 근거 |
|----------|-----------|------|
| A+B만 구현 | Level 3+ | 프로세스 정의 + 기계적 강제이지만, 정량 관리 부재 |
| A+B+C 분리 구현 | Level 4 | 정량 측정 추가. 하지만 측정→개선의 자동 연결이 없으면 Level 4 상단 |
| A+B+C 통합 루프 | **Level 4~5** | 측정 기반 지속적 개선이 자동화되면 Level 5 진입 가능 |

### 3.3 비교 매트릭스 (설계안 반영 후)

| 도구 | CMMI | 요구사항 | 설계 | 구현 | 검증 | 품질보증 | 측정 | 구성관리 |
|------|------|---------|------|------|------|---------|------|---------|
| Spec Kit (83K) | L2 | O | O | O | | | | |
| BMAD (43K) | L2~3 | O | O | O | triangle | | | |
| OpenSpec (35K) | L2 | O | O | O | triangle | | | |
| Hive (10K) | L2 | | | O | | | | |
| Kiro (3K) | L3 | O | O | O | triangle | triangle | | |
| Entrix (31) | L3~4 | | | | O | O | | |
| Scorecard (14) | L4 | | | | | triangle | O | |
| Reins (6) | L2~3 | | | | | triangle | triangle | O |
| **spec-recipe v0.9.0** | **L4~5** | **O** | **O** | **O** | **O** | **O** | **O** | triangle |

**고유 포지션**: spec-recipe는 요구사항부터 측정까지 6개 프로세스를 커버하는 유일한 도구가 될 수 있다. 다른 도구들은 최대 3~4개 프로세스만 커버한다.

---

## 4. 종합 권고 사항

### 4.1 설계안 수정 권고 (A+B)

| # | 권고 | 우선순위 | 근거 |
|---|------|---------|------|
| R1 | constraint에 `depth` 필드 추가 (fast/normal/deep) | 높음 | Entrix 참조. regex 한계 보완 |
| R2 | constraint 변경 시 agent 규칙 파일 자동 재생성 hook | 높음 | constraint ↔ agent 규칙 간 drift 방지 |
| R3 | feedback 내용을 agent 규칙 파일에 인라인 주입 | 높음 | agent의 "파일 확인" 행동 의존도 제거 |
| R4 | 교정 시도 횟수 상한 + ESCALATE 상태 | 중간 | 무한 루프 방지 |
| R5 | Watcher에 debounce 메커니즘 명시 | 중간 | 과도한 검증 실행 방지 |
| R6 | `spec-recipe discover-conventions` 명령어 | 낮음 | Agent OS 참조. convention 작성 진입장벽 낮춤 |

### 4.2 C(측정) 통합 권고

| # | 권고 | 우선순위 | 근거 |
|---|------|---------|------|
| R7 | `.spec-recipe/metrics/` 디렉토리에 검증 결과 누적 | 높음 | A+B+C 통합의 기반 |
| R8 | 기본 추적 지표 정의 (위반 건수 추이, 준수율, 교정 소요) | 높음 | Level 4 진입 조건 |
| R9 | milestone 종료 시 자동 리포트 생성 | 중간 | 정량 관리의 가시화 |
| R10 | 반복 패턴 → constraint 자동 제안 (Level 5 방향) | 낮음(장기) | 측정→개선 자동 연결 |

### 4.3 구현 우선순위 재편성 제안

설계안의 Phase 1/2/3을 다음과 같이 재편성하는 것을 권고한다:

**Phase 1: 제약 체계 + 기본 주입 + 최소 측정** (핵심)
- constraints/ 디렉토리 + YAML 스키마 + depth 필드
- 기본 invariant + principles 자동 변환
- build.py 확장: constraint → agent 규칙 파일 + 자동 재생성 hook
- metrics/ 디렉토리 + 기본 지표 수집 시작 (R7, R8)

**Phase 2: 피드백 루프 + 교정 강화** (핵심)
- feedback/ + current.md 관리
- pre-commit 확장: HALT/BLOCK/WARN + 미해결 HALT 전체 차단
- agent 규칙 파일에 feedback 인라인 주입 (R3)
- 교정 시도 상한 + ESCALATE (R4)

**Phase 3: 고급 기능** (선택)
- Watcher (debounce 포함)
- discover-conventions
- milestone 리포트 자동 생성
- 반복 패턴 분석

---

## 5. 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 설계 과잉 (over-engineering) | 중 | 높음 | Phase 1을 최소 기능으로 한정, 실증 후 확장 |
| agent가 규칙 파일을 무시 | 높음 | 중 | pre-commit 기계적 차단이 최종 방어선. agent 준수는 보너스. |
| constraint YAML 작성 부담 | 중 | 중 | 기본 규칙 세트 제공 + discover-conventions 자동화 |
| 실증 부재로 이론에 머무름 | 높음 | 높음 | Phase 1 완료 후 반드시 labor 프로젝트에 적용 테스트 |

---

## 6. 결론

spec-recipe는 현재 Level 3(Defined) 수준의 메타 프레임워크다. 설계안(A+B)이 구현되면 Level 3+로 올라가고, C(측정)까지 통합되면 Level 4~5를 목표할 수 있다.

가장 중요한 것은 **"원칙 선언 → agent 주입 → 기계적 강제 → 위반 피드백 → 측정 → 개선"의 전 구간 파이프라인**이다. 현존하는 어떤 도구도 이 전 구간을 커버하지 못한다. Spec Kit/OpenSpec/BMAD는 전반부(선언~주입), Kiro는 중반부(주입~피드백), Scorecard는 후반부(측정)만 다룬다.

spec-recipe가 이 전 구간을 연결하면, 단순한 도구가 아닌 "하네스 엔지니어링의 참조 아키텍처"로 자리잡을 수 있다.

다만, 이론적 완성도와 실증 사이의 간극을 경계해야 한다. Phase 1의 최소 구현을 빠르게 labor 프로젝트에 적용하여 현실성을 검증하는 것이 최우선이다.
