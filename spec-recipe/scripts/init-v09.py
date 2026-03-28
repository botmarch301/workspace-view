#!/usr/bin/env python3
"""
spec-recipe v0.9.0 프로젝트 초기화 [Recipe-only → Kitchen 초기화]
Kitchen 환경을 세팅한다:
- .spec-recipe/ 디렉토리 구조 생성
- 기본 constraint 복사 (invariants + principles)
- feedback/ 초기화
- issues/ 초기화
- metrics/ 초기화
- pre-commit hook 설치
- agent 규칙 파일 최초 빌드
"""

import os
import sys
import shutil
from pathlib import Path

# 이 스크립트 기준으로 spec-recipe 루트 찾기
SCRIPT_DIR = Path(__file__).parent
RECIPE_ROOT = SCRIPT_DIR.parent  # spec-recipe/ 디렉토리


def create_directory_structure(project_root):
    """Kitchen 디렉토리 구조를 생성한다."""
    dirs = [
        ".spec-recipe/constraints/invariants",
        ".spec-recipe/constraints/principles",
        ".spec-recipe/constraints/conventions",
        ".spec-recipe/constraints/exceptions",
        ".spec-recipe/feedback",
        ".spec-recipe/feedback/history",
        ".spec-recipe/issues",
        ".spec-recipe/issues/archive",
        ".spec-recipe/metrics",
        ".spec-recipe/metrics/runs",
        ".spec-recipe/metrics/reports",
        "spec/0-context",
        "spec/1-requirements",
        "spec/2-design",
        "spec/3-plan",
        "spec/4-manual",
        "decisions",
    ]

    for d in dirs:
        path = project_root / d
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [dir] {d}/")


def copy_default_constraints(project_root):
    """기본 constraint 파일을 Kitchen에 복사한다."""
    source_constraints = RECIPE_ROOT / "constraints"
    target_constraints = project_root / ".spec-recipe" / "constraints"

    for layer in ["invariants", "principles"]:
        source_dir = source_constraints / layer
        target_dir = target_constraints / layer
        if not source_dir.exists():
            continue
        for yml_file in source_dir.glob("*.yml"):
            target_file = target_dir / yml_file.name
            if not target_file.exists():
                shutil.copy2(yml_file, target_file)
                print(f"  [constraint] {layer}/{yml_file.name}")
            else:
                print(f"  [skip] {layer}/{yml_file.name} (이미 존재)")


def init_feedback(project_root):
    """feedback/current.md를 초기화한다."""
    feedback_file = project_root / ".spec-recipe" / "feedback" / "current.md"
    if not feedback_file.exists():
        feedback_file.write_text("# Pending Feedback (자동 생성 - 수동 수정 금지)\n\n미해결 위반 없음.\n")
        print("  [feedback] current.md initialized")


def init_issues(project_root):
    """issues/registry.md를 초기화한다."""
    registry_file = project_root / ".spec-recipe" / "issues" / "registry.md"
    if not registry_file.exists():
        registry_file.write_text(
            "# Issue Registry\n"
            "> 자동/수동 관리. Phase gate에서 open 이슈 확인 필수.\n\n"
            "현재 open 이슈 없음.\n"
        )
        print("  [issues] registry.md initialized")


def init_metrics(project_root):
    """metrics 디렉토리를 초기화한다."""
    summary_file = project_root / ".spec-recipe" / "metrics" / "summary.json"
    if not summary_file.exists():
        import json
        summary = {
            "version": "0.9.0",
            "updated_at": "",
            "constraint_hash": "",
            "counters": {
                "invariant_violations": 0,
                "principle_violations": 0,
                "convention_violations": 0,
                "active_exceptions": 0,
                "expired_exceptions": 0,
                "open_issues": 0,
                "escalated_issues": 0,
            },
            "rates": {
                "principle_compliance_rate": 0,
                "convention_compliance_rate": 0,
                "traceability_coverage": 0,
                "spec_code_drift_count": 0,
            },
            "remediation": {
                "avg_time_seconds": 0,
                "avg_attempts": 0,
                "total_completed": 0,
                "total_escalated": 0,
            },
            "last_phase_gate": {},
        }
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print("  [metrics] summary.json initialized")

    # .gitignore for runs/
    gitignore = project_root / ".spec-recipe" / "metrics" / "runs" / ".gitkeep"
    gitignore.touch()

    gi_file = project_root / ".spec-recipe" / "metrics" / ".gitignore"
    if not gi_file.exists():
        gi_file.write_text("runs/*\n!runs/.gitkeep\n")
        print("  [metrics] .gitignore for runs/ created")


def install_pre_commit_hook(project_root):
    """pre-commit hook을 설치한다."""
    hook_source = RECIPE_ROOT / "scripts" / "pre-commit"
    hook_target = project_root / ".git" / "hooks" / "pre-commit"

    if not (project_root / ".git").exists():
        print("  [hook] .git 디렉토리 없음 — hook 설치 건너뜀")
        return

    if hook_target.exists():
        print("  [hook] pre-commit hook 이미 존재 — 건너뜀 (수동 업데이트 필요)")
        return

    shutil.copy2(hook_source, hook_target)
    os.chmod(hook_target, 0o755)
    print("  [hook] pre-commit hook 설치 완료")


def copy_scripts(project_root):
    """검증 스크립트를 Kitchen에 복사한다."""
    scripts = [
        "verify-phase-separation.py",
        "verify-constraints.py",
        "build-agent-rules.py",
        "remediation-tracker.py",
    ]

    target_dir = project_root / "scripts"
    target_dir.mkdir(parents=True, exist_ok=True)

    for script_name in scripts:
        source = RECIPE_ROOT / "scripts" / script_name
        target = target_dir / script_name
        if source.exists():
            shutil.copy2(source, target)
            print(f"  [script] {script_name}")


def run_initial_build(project_root):
    """초기 agent 규칙 파일을 빌드한다."""
    build_script = project_root / "scripts" / "build-agent-rules.py"
    if build_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(build_script)],
            cwd=str(project_root),
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  [build] AGENTS.md + CLAUDE.md 생성 완료")
        else:
            print(f"  [build] WARNING: {result.stderr[:200]}")


def main():
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1]).resolve()
    else:
        project_root = Path.cwd()

    print(f"spec-recipe v0.9.0 초기화: {project_root}")
    print(f"Recipe 소스: {RECIPE_ROOT}")
    print()

    print("[1/7] 디렉토리 구조 생성")
    create_directory_structure(project_root)
    print()

    print("[2/7] 기본 constraint 복사")
    copy_default_constraints(project_root)
    print()

    print("[3/7] Feedback 초기화")
    init_feedback(project_root)
    print()

    print("[4/7] Issues 초기화")
    init_issues(project_root)
    print()

    print("[5/7] Metrics 초기화")
    init_metrics(project_root)
    print()

    print("[6/7] 스크립트 복사 + Hook 설치")
    copy_scripts(project_root)
    install_pre_commit_hook(project_root)
    print()

    print("[7/7] 초기 빌드")
    run_initial_build(project_root)
    print()

    print("=" * 50)
    print("spec-recipe v0.9.0 초기화 완료!")
    print()
    print("다음 단계:")
    print("  1. spec/0-context/glossary.md 작성 (Glossary-First)")
    print("  2. spec/1-requirements/ 에 요구사항 작성")
    print("  3. .spec-recipe/constraints/conventions/ 에 프로젝트 컨벤션 추가")
    print("  4. git add -A && git commit -m '[init] spec-recipe 초기화'")
    print("=" * 50)


if __name__ == "__main__":
    main()
