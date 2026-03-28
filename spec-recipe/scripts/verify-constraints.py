#!/usr/bin/env python3
"""
Constraint 검증 엔진 [Kitchen-only]
constraint YAML을 파싱하여 staged 파일에 대해 검증을 실행한다.
HALT(invariant), BLOCK(principle/convention)으로 분류.
Ref: ADR-0002, CORE-CST-001
"""

import os
import re
import sys
import subprocess
import hashlib
import json
from pathlib import Path
from datetime import datetime, date

try:
    import yaml
except ImportError:
    print("WARNING: PyYAML not installed. Constraint verification skipped.")
    sys.exit(0)


CONSTRAINTS_DIR = ".spec-recipe/constraints"
FEEDBACK_FILE = ".spec-recipe/feedback/current.md"
METRICS_DIR = ".spec-recipe/metrics/runs"


def load_constraints(layer=None):
    """constraint YAML 파일들을 로드한다."""
    constraints = []
    base = Path(CONSTRAINTS_DIR)

    dirs = [layer] if layer else ["invariants", "principles", "conventions"]
    for d in dirs:
        dir_path = base / d
        if not dir_path.exists():
            continue
        for yml_file in sorted(dir_path.glob("*.yml")):
            with open(yml_file, "r") as f:
                try:
                    constraint = yaml.safe_load(f)
                    if constraint:
                        constraint["_file"] = str(yml_file)
                        constraints.append(constraint)
                except yaml.YAMLError as e:
                    print(f"WARNING: YAML 파싱 오류: {yml_file}: {e}")
    return constraints


def load_exceptions():
    """활성 예외 목록을 로드한다."""
    exceptions = {}
    exc_dir = Path(CONSTRAINTS_DIR) / "exceptions"
    if not exc_dir.exists():
        return exceptions

    today = date.today()
    for yml_file in exc_dir.glob("*.yml"):
        with open(yml_file, "r") as f:
            try:
                exc = yaml.safe_load(f)
                if not exc:
                    continue

                # 만료 확인
                expires = exc.get("expires")
                if expires:
                    if isinstance(expires, str):
                        expires = date.fromisoformat(expires)
                    if expires < today:
                        continue  # 만료된 예외는 무시

                target = exc.get("target_constraint", "")
                if target not in exceptions:
                    exceptions[target] = []
                exceptions[target].append(exc)
            except yaml.YAMLError:
                pass
    return exceptions


def check_expired_exceptions():
    """만료된 예외가 있는지 확인한다. 만료된 예외가 있으면 HALT."""
    exc_dir = Path(CONSTRAINTS_DIR) / "exceptions"
    if not exc_dir.exists():
        return []

    expired = []
    today = date.today()
    for yml_file in exc_dir.glob("*.yml"):
        with open(yml_file, "r") as f:
            try:
                exc = yaml.safe_load(f)
                if not exc:
                    continue
                expires = exc.get("expires")
                if expires:
                    if isinstance(expires, str):
                        expires = date.fromisoformat(expires)
                    if expires < today:
                        expired.append({
                            "id": exc.get("id", "?"),
                            "target": exc.get("target_constraint", "?"),
                            "expired": str(expires),
                            "file": str(yml_file),
                        })
            except yaml.YAMLError:
                pass
    return expired


def get_staged_files():
    """git staging 영역의 파일 목록을 반환한다."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def matches_scope(filepath, scope):
    """파일이 constraint의 scope에 해당하는지 확인한다."""
    from fnmatch import fnmatch

    files_pattern = scope.get("files", "**/*")
    exclude = scope.get("exclude", [])

    if isinstance(files_pattern, str):
        files_pattern = [files_pattern]

    # exclude 확인
    for exc_pattern in exclude:
        if fnmatch(filepath, exc_pattern):
            return False

    # files 패턴 확인
    for pattern in files_pattern:
        if fnmatch(filepath, pattern):
            return True

    return False


def is_excepted(constraint_id, filepath, line, exceptions):
    """해당 파일/라인이 예외로 등록되어 있는지 확인한다."""
    if constraint_id not in exceptions:
        return False

    for exc in exceptions[constraint_id]:
        exc_files = exc.get("scope", {}).get("files", [])
        exc_lines = exc.get("scope", {}).get("lines", [])

        if filepath in exc_files:
            if not exc_lines or line in exc_lines:
                return True
    return False


def check_regex(filepath, patterns, exceptions, constraint_id):
    """regex 기반 검증을 수행한다."""
    violations = []
    try:
        with open(filepath, "r", errors="ignore") as f:
            for line_num, line_content in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line_content):
                        if not is_excepted(constraint_id, filepath, line_num, exceptions):
                            violations.append({
                                "file": filepath,
                                "line": line_num,
                                "pattern": pattern,
                                "content": line_content.strip()[:100],
                            })
    except (IOError, OSError):
        pass
    return violations


def run_verification(depth="normal"):
    """전체 constraint 검증을 실행한다."""
    staged_files = get_staged_files()
    if not staged_files:
        return {"halt": [], "block": [], "pass": True}

    constraints = load_constraints()
    exceptions = load_exceptions()

    halt_violations = []
    block_violations = []

    # 만료된 예외 확인
    expired = check_expired_exceptions()
    for exp in expired:
        halt_violations.append({
            "constraint_id": exp["target"],
            "type": "expired_exception",
            "detail": f"예외 {exp['id']}이 {exp['expired']}에 만료됨. 예외를 갱신하거나 위반을 교정하세요.",
            "file": exp["file"],
        })

    for constraint in constraints:
        cid = constraint.get("id", "?")
        layer = constraint.get("layer", "convention")
        scope = constraint.get("scope", {})
        detection = constraint.get("detection", {})

        depth_config = detection.get(depth, detection.get("normal", {}))
        if not depth_config:
            continue

        method = depth_config.get("method", "")
        patterns = depth_config.get("patterns", [])

        # 해당 파일 필터링
        target_files = [f for f in staged_files if matches_scope(f, scope)]
        if not target_files:
            continue

        if method == "regex" and patterns:
            for filepath in target_files:
                violations = check_regex(filepath, patterns, exceptions, cid)
                for v in violations:
                    entry = {
                        "constraint_id": cid,
                        "constraint_name": constraint.get("name", ""),
                        "file": v["file"],
                        "line": v["line"],
                        "detail": v["content"],
                        "remediation": constraint.get("remediation", ""),
                    }
                    if layer == "invariant":
                        halt_violations.append(entry)
                    else:
                        block_violations.append(entry)

        elif method == "script":
            command = depth_config.get("command", "")
            if command:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True
                )
                if result.returncode != 0:
                    entry = {
                        "constraint_id": cid,
                        "constraint_name": constraint.get("name", ""),
                        "file": "(script)",
                        "detail": result.stdout[:500] if result.stdout else result.stderr[:500],
                        "remediation": constraint.get("remediation", ""),
                    }
                    if layer == "invariant":
                        halt_violations.append(entry)
                    else:
                        block_violations.append(entry)

    return {
        "halt": halt_violations,
        "block": block_violations,
        "pass": len(halt_violations) == 0 and len(block_violations) == 0,
    }


def update_feedback(results):
    """feedback/current.md를 갱신한다."""
    feedback_path = Path(FEEDBACK_FILE)
    feedback_path.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# Pending Feedback (자동 생성 - 수동 수정 금지)\n\n"]

    for v in results["halt"]:
        lines.append(f"## HALT: {v['constraint_id']} {v.get('constraint_name', '')}\n")
        lines.append(f"- **파일**: {v['file']}")
        if v.get('line'):
            lines[-1] += f":{v['line']}"
        lines.append(f"\n- **감지**: {v['detail']}\n")
        if v.get('remediation'):
            lines.append(f"- **교정**: {v['remediation'].strip().split(chr(10))[0]}\n")
        lines.append(f"- **상태**: 미해결\n\n")

    for v in results["block"]:
        lines.append(f"## BLOCK: {v['constraint_id']} {v.get('constraint_name', '')}\n")
        lines.append(f"- **파일**: {v['file']}")
        if v.get('line'):
            lines[-1] += f":{v['line']}"
        lines.append(f"\n- **감지**: {v['detail']}\n")
        if v.get('remediation'):
            lines.append(f"- **교정**: {v['remediation'].strip().split(chr(10))[0]}\n")
        lines.append(f"- **상태**: 미해결\n\n")

    if not results["halt"] and not results["block"]:
        lines.append("미해결 위반 없음.\n")

    with open(feedback_path, "w") as f:
        f.writelines(lines)


def main():
    results = run_verification(depth="normal")

    update_feedback(results)

    if results["halt"]:
        print("=" * 60)
        print(f"HALT: Invariant 위반 {len(results['halt'])}건 — 전체 커밋 차단")
        print("=" * 60)
        for v in results["halt"]:
            print(f"  [{v['constraint_id']}] {v.get('file', '')}:{v.get('line', '')}")
            print(f"    {v['detail']}")
        print()
        print("교정 후 다시 커밋하세요.")
        return 1

    if results["block"]:
        print("=" * 60)
        print(f"BLOCK: Principle/Convention 위반 {len(results['block'])}건 — 커밋 차단")
        print("=" * 60)
        for v in results["block"]:
            print(f"  [{v['constraint_id']}] {v.get('file', '')}:{v.get('line', '')}")
            print(f"    {v['detail']}")
        print()
        print("교정 후 다시 커밋하세요.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
