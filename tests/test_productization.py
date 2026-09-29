from __future__ import annotations

import subprocess
from pathlib import Path


def git_commit_all(path: Path, message: str = "fixture: persist product binding") -> None:
    subprocess.run(["git", "config", "user.name", "Harness v2 Product Fixture"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "harness-v2-product@example.invalid"], cwd=path, check=True
    )
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, capture_output=True)
