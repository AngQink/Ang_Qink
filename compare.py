"""Run the public tests against reference implementations in temporary copies."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
QUESTIONS = ROOT / "questions"
ANSWERS = ROOT / "answers"

PYTEST_PROBLEMS = {"binary-ledger-codec", "transactional-kv-recovery"}


def compare(slug):
    question = QUESTIONS / slug
    reference = ANSWERS / slug / "reference"
    with TemporaryDirectory(prefix="algorithm-benchmark-") as temp:
        work = Path(temp) / slug
        shutil.copytree(question, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        shutil.copytree(reference, work, dirs_exist_ok=True)
        if slug in PYTEST_PROBLEMS:
            test = ["-m", "pytest", "public_tests", "-q", "-p", "no:cacheprovider"]
        else:
            test = ["-m", "unittest", "discover", "-s", "public_tests", "-v"]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        command = [sys.executable, "-B", *test]
        print(f"\n[{slug}]", flush=True)
        return subprocess.run(command, cwd=work, env=env, check=False).returncode == 0


def main():
    available = sorted(path.name for path in QUESTIONS.iterdir() if path.is_dir()) if QUESTIONS.is_dir() else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", nargs="*", metavar="PROBLEM", help="one or more problem directory names")
    args = parser.parse_args()
    if not available or not ANSWERS.is_dir():
        parser.error("Place questions/ and answers/ next to this script.")
    chosen = list(dict.fromkeys(args.problem)) or available
    for slug in chosen:
        if slug not in available or not (ANSWERS / slug / "reference").is_dir():
            parser.error(f"Unknown problem or missing reference: {slug}")
    results = {slug: compare(slug) for slug in chosen}
    failed = [slug for slug, passed in results.items() if not passed]
    print(f"\nPassed {len(results) - len(failed)}/{len(results)} problem packages.")
    for slug in failed:
        print(f"FAILED {slug}")
    return bool(failed)


if __name__ == "__main__":
    sys.exit(main())
