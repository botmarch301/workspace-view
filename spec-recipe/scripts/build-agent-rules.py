#!/usr/bin/env python3
"""
Agent 규칙 파일 빌드 스크립트 [Recipe-only]
constraint YAML → AGENTS.md / CLAUDE.md 변환.
Ref: ADR-0004, ADR-0006
"""

import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip install pyyaml")
    sys.exit(1)


CONSTRAINTS_DIR = ".spec-recipe/constraints"
FEEDBACK_FILE = ".spec-recipe/feedback/current.md"


def compute_constraint_hash():
    """constraints/ 디렉토리 전체의 해시를 계산한다."""
    hasher = hashlib.sha256()
    base = Path(CONSTRAINTS_DIR)
    for yml_file in sorted(base.rglob("*.yml")):
        with open(yml_file, "rb") as f:
            hasher.update(f.read())
    return hasher.hexdigest()[:8]


def load_constraints_by_layer():
    """계층별로 constraint를 로드한다."""
    layers = {"invariants": [], "principles": [], "conventions": []}
    base = Path(CONSTRAINTS_DIR)

    for layer_name in layers:
        dir_path = base / layer_name
        if not dir_path.exists():
            continue
        for yml_file in sorted(dir_path.glob("*.yml")):
            with open(yml_file, "r") as f:
                try:
                    constraint = yaml.safe_load(f)
                    if constraint:
                        layers[layer_name].append(constraint)
                except yaml.YAMLError as e:
                    print(f"WARNING: {yml_file}: {e}")

    return layers


def load_pending_feedback():
    """미해결 피드백을 로드한다."""
    path = Path(FEEDBACK_FILE)
    if not path.exists():
        return ""

    content = path.read_text()
    if "미해결 위반 없음" in content:
        return ""
    return content


def render_constraints_section(constraints, header, include_remediation=False):
    """constraint 목록을 마크다운 섹션으로 렌더링한다."""
    if not constraints:
        return ""

    lines = [f"\n## {header}\n"]
    for c in constraints:
        name = c.get("name", c.get("id", "?"))
        cid = c.get("id", "?")
        lines.append(f"- **{cid}**: {name}")
        if include_remediation and c.get("remediation"):
            # remediation 첫 줄만 포함
            first_line = c["remediation"].strip().split("\n")[0]
            lines.append(f"  - {first_line}")
    lines.append("")
    return "\n".join(lines)


def render_feedback_section(feedback_content):
    """미해결 피드백을 인라인 섹션으로 렌더링한다."""
    if not feedback_content:
        return ""

    lines = ["\n## PENDING VIOLATIONS (자동 생성 - 교정 필요)\n"]
    # feedback에서 HALT/BLOCK 항목만 추출
    for line in feedback_content.split("\n"):
        if line.startswith("## HALT:") or line.startswith("## BLOCK:"):
            lines.append(f"- {line.replace('## ', '').strip()}")
        elif line.startswith("- **파일**:"):
            lines.append(f"  {line.strip()}")
    if len(lines) > 1:
        lines.append("")
        lines.append("미해결 HALT가 있는 상태에서 다른 작업을 진행하지 마세요.")
        lines.append("")
        return "\n".join(lines)
    return ""


def build_agents_md(layers, constraint_hash, feedback_content):
    """Codex AGENTS.md를 생성한다."""
    lines = [
        f"<!-- spec-recipe:constraint-hash:{constraint_hash} -->",
        "<!-- 이 파일은 spec-recipe에서 자동 생성됩니다. 수동 수정하지 마세요. -->",
        f"<!-- 재생성: python3 scripts/build-agent-rules.py -->",
        f"<!-- 생성일: {datetime.now().isoformat()} -->",
        "",
        "# Project Rules",
        "",
    ]

    # 미해결 피드백 (최상단)
    feedback_section = render_feedback_section(feedback_content)
    if feedback_section:
        lines.append(feedback_section)

    # Invariants
    lines.append(render_constraints_section(
        layers["invariants"], "Absolute Rules (위반 시 즉시 중단)", True
    ))

    # Principles
    lines.append(render_constraints_section(
        layers["principles"], "Development Principles (위반 시 커밋 차단)", True
    ))

    # Conventions
    lines.append(render_constraints_section(
        layers["conventions"], "Conventions (위반 시 커밋 차단)", True
    ))

    return "\n".join(lines)


def build_claude_md(layers, constraint_hash, feedback_content):
    """Claude Code CLAUDE.md를 생성한다."""
    lines = [
        f"<!-- spec-recipe:constraint-hash:{constraint_hash} -->",
        "<!-- 이 파일은 spec-recipe에서 자동 생성됩니다. 수동 수정하지 마세요. -->",
        f"<!-- 재생성: python3 scripts/build-agent-rules.py -->",
        f"<!-- 생성일: {datetime.now().isoformat()} -->",
        "",
        "# CLAUDE.md - Project Instructions",
        "",
    ]

    # 미해결 피드백 (최상단)
    feedback_section = render_feedback_section(feedback_content)
    if feedback_section:
        lines.append(feedback_section)

    # Security Rules
    lines.append(render_constraints_section(
        layers["invariants"], "Security Rules (절대 위반 불가)", True
    ))

    # Principles
    lines.append(render_constraints_section(
        layers["principles"], "Principles", True
    ))

    # Conventions
    lines.append(render_constraints_section(
        layers["conventions"], "Conventions", True
    ))

    # Feedback check instruction
    lines.append("\n## Feedback Check")
    lines.append("작업 시작 전 `.spec-recipe/feedback/current.md`를 확인하세요.")
    lines.append("미해결 HALT 항목이 있으면 해당 항목부터 교정합니다.")
    lines.append("")

    return "\n".join(lines)


def build_index_yml(layers, constraint_hash):
    """constraints/index.yml을 생성한다."""
    index = {
        "generated_at": datetime.now().isoformat(),
        "constraint_hash": constraint_hash,
        "invariants": [],
        "principles": [],
        "conventions": [],
        "exceptions": [],
        "stats": {
            "total": 0,
            "invariants": 0,
            "principles": 0,
            "conventions": 0,
            "exceptions": 0,
        }
    }

    for layer_name, constraints in layers.items():
        for c in constraints:
            entry = {
                "id": c.get("id", "?"),
                "name": c.get("name", ""),
                "severity": c.get("severity", "block"),
            }
            index[layer_name].append(entry)
            index["stats"][layer_name] += 1
            index["stats"]["total"] += 1

    return yaml.dump(index, default_flow_style=False, allow_unicode=True)


def main():
    # constraint 로드
    layers = load_constraints_by_layer()
    constraint_hash = compute_constraint_hash()
    feedback_content = load_pending_feedback()

    total = sum(len(v) for v in layers.values())
    print(f"Loaded {total} constraints (hash: {constraint_hash})")

    # AGENTS.md 생성
    agents_md = build_agents_md(layers, constraint_hash, feedback_content)
    with open("AGENTS.md", "w") as f:
        f.write(agents_md)
    print(f"  -> AGENTS.md generated")

    # CLAUDE.md 생성
    claude_md = build_claude_md(layers, constraint_hash, feedback_content)
    with open("CLAUDE.md", "w") as f:
        f.write(claude_md)
    print(f"  -> CLAUDE.md generated")

    # index.yml 생성
    index_yml = build_index_yml(layers, constraint_hash)
    index_path = Path(CONSTRAINTS_DIR) / "index.yml"
    with open(index_path, "w") as f:
        f.write(index_yml)
    print(f"  -> {index_path} generated")

    print(f"\nBuild complete. Constraint hash: {constraint_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
