"""Check this problem's reference implementation using its public tests."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    answer = Path(__file__).resolve().parent
    question = answer.parent / "题目"
    reference = answer / "reference"
    if not question.is_dir() or not reference.is_dir():
        raise SystemExit("Keep the 题目 and 答案 folders next to each other.")
    with TemporaryDirectory(prefix="algorithm-benchmark-") as temp:
        scratch = Path(temp)
        work = scratch / "problem"
        shutil.copytree(question, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        shutil.copytree(reference, work, dirs_exist_ok=True)
        options = ["-m", "unittest", "discover", "-s", "public_tests", "-v"]
        return subprocess.run(
            [sys.executable, "-B", *options],
            cwd=work,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        ).returncode


if __name__ == "__main__":
    sys.exit(main())
