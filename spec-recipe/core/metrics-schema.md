# Metrics Schema
> **ID**: CORE-MET-001
> **Version**: 0.9.0
> **Status**: Draft
> **Last Updated**: 2026-03-28
> **Scope**: [Kitchen-only]

---

## 1. 디렉토리 구조

```
.spec-recipe/
  metrics/
    summary.json        # git 추적 O — 현재 상태 스냅샷
    runs/               # git 추적 X — 상세 실행 기록
      .gitkeep
    reports/            # git 추적 O — milestone 리포트
```

## 2. summary.json 스키마

```json
{
  "version": "0.9.0",
  "updated_at": "2026-03-28T10:30:00Z",
  "constraint_hash": "a1b2c3d4",
  "counters": {
    "invariant_violations": 0,
    "principle_violations": 2,
    "convention_violations": 0,
    "active_exceptions": 1,
    "expired_exceptions": 0,
    "open_issues": 3,
    "escalated_issues": 0
  },
  "rates": {
    "principle_compliance_rate": 0.85,
    "convention_compliance_rate": 1.0,
    "traceability_coverage": 0.72,
    "spec_code_drift_count": 1
  },
  "remediation": {
    "avg_time_seconds": 3600,
    "avg_attempts": 1.5,
    "total_completed": 12,
    "total_escalated": 0
  },
  "last_phase_gate": {
    "gate": "PG-2",
    "result": "PASS",
    "timestamp": "2026-03-28T09:00:00Z"
  }
}
```

## 3. 개별 실행 기록 스키마 (runs/)

```json
{
  "run_id": "2026-03-28T10-30-00",
  "trigger": "pre-commit",
  "duration_ms": 1234,
  "results": {
    "invariants": {"total": 7, "pass": 7, "fail": 0},
    "principles": {"total": 7, "pass": 5, "fail": 2},
    "conventions": {"total": 0, "pass": 0, "fail": 0}
  },
  "violations": [
    {
      "constraint_id": "PRC-TRC-001",
      "file": "src/handlers/payment.py",
      "line": 42,
      "detail": "Implements: 태그 누락"
    }
  ],
  "phase_gate": null
}
```

## 4. 추적 지표

| 지표 | 설명 | 수집 시점 |
|------|------|----------|
| invariant_violations | Invariant 위반 건수 | 매 커밋 |
| principle_compliance_rate | Principle 준수율 (%) | 매 커밋 |
| convention_compliance_rate | Convention 준수율 (%) | 매 커밋 |
| traceability_coverage | 추적성 태그 커버율 (%) | 매 커밋 |
| spec_code_drift_count | 스펙-코드 불일치 건수 | Feature 완료 시 |
| remediation_time_avg | 평균 교정 소요 시간 | 교정 완료 시 |
| remediation_attempts_avg | 평균 교정 시도 횟수 | 교정 완료 시 |
| escalation_count | ESCALATE 발생 건수 | ESCALATE 발생 시 |
