#!/usr/bin/env python3
"""
교정 추적기 [Kitchen-only]
위반 → 교정 시도 → PASS/FAIL 추적.
교정 상한 초과 시 ESCALATE 상태로 전환.
Ref: ADR-0003 (교정 상한), CORE-MET-001
"""

import json
import sys
from pathlib import Path
from datetime import datetime

TRACKING_FILE = ".spec-recipe/feedback/remediation-tracking.json"
FEEDBACK_FILE = ".spec-recipe/feedback/current.md"
METRICS_DIR = ".spec-recipe/metrics/runs"
SUMMARY_FILE = ".spec-recipe/metrics/summary.json"

DEFAULT_MAX_ATTEMPTS = 3


def load_tracking():
    """교정 추적 데이터를 로드한다."""
    path = Path(TRACKING_FILE)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"violations": {}, "config": {"max_attempts": DEFAULT_MAX_ATTEMPTS}}


def save_tracking(data):
    """교정 추적 데이터를 저장한다."""
    path = Path(TRACKING_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_violation(constraint_id, file, line=None, detail=""):
    """위반을 기록하거나 기존 위반의 시도 횟수를 증가시킨다."""
    tracking = load_tracking()
    max_attempts = tracking["config"]["max_attempts"]

    key = f"{constraint_id}:{file}:{line or 0}"

    if key not in tracking["violations"]:
        tracking["violations"][key] = {
            "constraint_id": constraint_id,
            "file": file,
            "line": line,
            "detail": detail,
            "attempts": 0,
            "status": "open",
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
        }

    entry = tracking["violations"][key]
    entry["attempts"] += 1
    entry["last_seen"] = datetime.now().isoformat()

    if entry["attempts"] >= max_attempts and entry["status"] != "escalated":
        entry["status"] = "escalated"
        print(f"ESCALATE: {constraint_id} ({file}:{line}) — 교정 시도 {entry['attempts']}/{max_attempts}회 초과")
        print(f"  인간의 직접 개입이 필요합니다.")

    save_tracking(tracking)
    return entry


def resolve_violation(constraint_id, file, line=None):
    """위반이 교정되었음을 기록한다."""
    tracking = load_tracking()

    key = f"{constraint_id}:{file}:{line or 0}"

    if key in tracking["violations"]:
        entry = tracking["violations"][key]
        entry["status"] = "resolved"
        entry["resolved_at"] = datetime.now().isoformat()

        # 교정 소요 시간 계산
        first_seen = datetime.fromisoformat(entry["first_seen"])
        resolved_at = datetime.fromisoformat(entry["resolved_at"])
        entry["remediation_time_seconds"] = (resolved_at - first_seen).total_seconds()

        save_tracking(tracking)
        return entry

    return None


def get_escalated():
    """ESCALATE 상태의 위반 목록을 반환한다."""
    tracking = load_tracking()
    return [
        v for v in tracking["violations"].values()
        if v["status"] == "escalated"
    ]


def update_summary():
    """metrics/summary.json을 갱신한다."""
    tracking = load_tracking()
    summary_path = Path(SUMMARY_FILE)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    # 기존 summary 로드 또는 초기화
    if summary_path.exists():
        with open(summary_path, "r") as f:
            summary = json.load(f)
    else:
        summary = {
            "version": "0.9.0",
            "counters": {},
            "rates": {},
            "remediation": {},
            "last_phase_gate": {},
        }

    # 교정 통계 갱신
    violations = tracking["violations"]
    resolved = [v for v in violations.values() if v["status"] == "resolved"]
    escalated = [v for v in violations.values() if v["status"] == "escalated"]
    open_violations = [v for v in violations.values() if v["status"] in ("open",)]

    summary["updated_at"] = datetime.now().isoformat()
    summary["counters"]["open_issues"] = len(open_violations)
    summary["counters"]["escalated_issues"] = len(escalated)
    summary["remediation"]["total_completed"] = len(resolved)
    summary["remediation"]["total_escalated"] = len(escalated)

    if resolved:
        times = [v.get("remediation_time_seconds", 0) for v in resolved if v.get("remediation_time_seconds")]
        attempts = [v.get("attempts", 1) for v in resolved]
        summary["remediation"]["avg_time_seconds"] = sum(times) / len(times) if times else 0
        summary["remediation"]["avg_attempts"] = sum(attempts) / len(attempts) if attempts else 0

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    """CLI 인터페이스."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  remediation-tracker.py record <constraint_id> <file> [line] [detail]")
        print("  remediation-tracker.py resolve <constraint_id> <file> [line]")
        print("  remediation-tracker.py escalated")
        print("  remediation-tracker.py summary")
        return 1

    action = sys.argv[1]

    if action == "record":
        if len(sys.argv) < 4:
            print("ERROR: constraint_id와 file이 필요합니다.")
            return 1
        cid = sys.argv[2]
        file = sys.argv[3]
        line = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
        detail = sys.argv[5] if len(sys.argv) > 5 else ""
        entry = record_violation(cid, file, line, detail)
        print(f"Recorded: {cid} ({file}:{line}) — 시도 {entry['attempts']}회, 상태: {entry['status']}")

    elif action == "resolve":
        if len(sys.argv) < 4:
            print("ERROR: constraint_id와 file이 필요합니다.")
            return 1
        cid = sys.argv[2]
        file = sys.argv[3]
        line = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
        entry = resolve_violation(cid, file, line)
        if entry:
            print(f"Resolved: {cid} ({file}:{line}) — 시도 {entry['attempts']}회, 소요 {entry.get('remediation_time_seconds', 0):.0f}초")
        else:
            print(f"Not found: {cid} ({file}:{line})")

    elif action == "escalated":
        escalated = get_escalated()
        if escalated:
            print(f"ESCALATED 위반 {len(escalated)}건:")
            for v in escalated:
                print(f"  [{v['constraint_id']}] {v['file']}:{v.get('line', '')} — 시도 {v['attempts']}회")
        else:
            print("ESCALATED 위반 없음.")

    elif action == "summary":
        update_summary()
        print(f"Summary 갱신 완료: {SUMMARY_FILE}")

    else:
        print(f"Unknown action: {action}")
        return 1

    update_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
