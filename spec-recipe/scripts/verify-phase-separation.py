#!/usr/bin/env python3
"""
Phase Separation 검증 스크립트 [Kitchen-only]
커밋 시 4개 작업 영역의 동시 변경을 차단한다.
Ref: ADR-0007, CORE-PRC-001 Section 8
"""

import subprocess
import sys
import re

# 4개 경로 그룹 정의
PATH_GROUPS = {
    "specification": [
        ".spec-recipe/constraints/",
        "spec/0-context/",
        "spec/1-requirements/",
        "decisions/",
    ],
    "design": [
        "spec/2-design/",
        "spec/3-plan/",
    ],
    "development": [
        "src/",
        "lib/",
        "app/",
        "config/",
    ],
    "testing": [
        "tests/",
        "test/",
    ],
}

# 테스트 파일 패턴 (경로 그룹 외 추가 패턴)
TEST_PATTERNS = [
    r".*_test\.\w+$",
    r".*_spec\.\w+$",
    r".*/test_.*\.\w+$",
]

# 예외: 이 파일들은 어느 영역과도 동시 커밋 가능
EXEMPT_PATTERNS = [
    r"README\.md$",
    r"CHANGELOG\.md$",
    r"LICENSE",
    r"\.gitignore$",
    r"\.spec-recipe/metrics/",
    r"\.spec-recipe/feedback/",
    r"\.spec-recipe/issues/",
]

# init 커밋 태그 (예외)
INIT_COMMIT_TAG = "[init]"


def get_staged_files():
    """git staging 영역의 파일 목록을 반환한다."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def get_commit_message():
    """현재 커밋 메시지를 반환한다.
    pre-commit 시점에서는 COMMIT_EDITMSG가 없을 수 있으므로,
    커밋 메시지 검증은 commit-msg hook에서 수행한다.
    이 함수는 commit-msg hook에서 인자로 전달된 파일을 읽는다."""
    # commit-msg hook에서 호출 시: sys.argv에 메시지 파일 경로가 전달됨
    import sys
    if len(sys.argv) > 1 and os.path.exists(sys.argv[-1]):
        try:
            with open(sys.argv[-1], "r") as f:
                return f.read().strip()
        except (IOError, OSError):
            pass
    # pre-commit 시점: 커밋 메시지 아직 없음
    return ""


def classify_file(filepath):
    """파일을 4개 영역 중 하나로 분류한다. 분류 불가 시 None."""
    # 예외 패턴 확인
    for pattern in EXEMPT_PATTERNS:
        if re.search(pattern, filepath):
            return None  # 예외 파일은 분류하지 않음

    # 테스트 패턴 우선 확인 (경로와 무관하게 파일명 패턴으로)
    for pattern in TEST_PATTERNS:
        if re.search(pattern, filepath):
            return "testing"

    # 경로 그룹으로 분류
    for group_name, prefixes in PATH_GROUPS.items():
        for prefix in prefixes:
            if filepath.startswith(prefix):
                return group_name

    return None  # 분류 불가 (제약 대상 아님)


def validate_commit_tag(message, detected_groups):
    """커밋 메시지의 영역 태그와 실제 변경 영역이 일치하는지 확인한다."""
    tag_map = {
        "specification": "[spec]",
        "design": "[design]",
        "development": "[dev]",
        "testing": "[test]",
    }

    if not detected_groups:
        return True, ""

    expected_tag = tag_map.get(list(detected_groups)[0], "")
    if expected_tag and expected_tag not in message:
        return False, f"커밋 메시지에 영역 태그 '{expected_tag}'가 필요합니다."

    return True, ""


def main():
    staged_files = get_staged_files()
    if not staged_files:
        return 0

    commit_msg = get_commit_message()

    # init 커밋은 예외
    if INIT_COMMIT_TAG in commit_msg:
        return 0

    # 파일별 영역 분류
    file_groups = {}
    detected_groups = set()

    for filepath in staged_files:
        group = classify_file(filepath)
        if group:
            detected_groups.add(group)
            if group not in file_groups:
                file_groups[group] = []
            file_groups[group].append(filepath)

    # 2개 이상 영역 동시 변경 확인
    if len(detected_groups) > 1:
        print("=" * 60)
        print("BLOCK: Phase Separation 위반 (ADR-0007)")
        print("=" * 60)
        print(f"동일 커밋에 {len(detected_groups)}개 영역의 변경이 포함되어 있습니다.")
        print()
        for group_name in sorted(detected_groups):
            print(f"  [{group_name}]")
            for f in file_groups[group_name][:5]:
                print(f"    - {f}")
            if len(file_groups[group_name]) > 5:
                print(f"    ... 외 {len(file_groups[group_name]) - 5}개")
        print()
        print("각 영역의 변경은 독립된 커밋으로 분리해야 합니다.")
        print("커밋 메시지 태그: [spec], [design], [dev], [test]")
        print("=" * 60)
        return 1

    # 커밋 메시지 태그 확인
    if commit_msg and detected_groups:
        valid, msg = validate_commit_tag(commit_msg, detected_groups)
        if not valid:
            print(f"BLOCK: {msg}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
