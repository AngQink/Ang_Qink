"""Run this problem's original evaluation suite on Windows."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def run(candidate, output, config):
    mode = config["runner"]
    entrypoint = config["entrypoint"]
    if mode == "directory":
        if not candidate.is_dir() or not (candidate / entrypoint).is_file():
            raise SystemExit(f"Choose a directory containing {entrypoint}.")
    else:
        if candidate.is_dir():
            candidate /= entrypoint
        if not candidate.is_file():
            raise SystemExit(f"Cannot find candidate file: {candidate}")

    if mode == "frozen":
        args = ["run_grader.py", "--submission", str(candidate), "--output", str(output)]
    else:
        for relative, digest in config["files"].items():
            path = (ROOT / relative).resolve()
            if ROOT not in path.parents or sha256(path.read_bytes()).hexdigest() != digest:
                raise SystemExit(f"Evaluation file changed: {relative}")
        args = ["judge.py", "--candidate", str(candidate), "--out", str(output)]

    command = [sys.executable, "-B", str(ROOT / "judge" / args[0]), *args[1:]]
    result = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONUTF8": "1"}, check=False)
    if result.returncode:
        return result.returncode
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    count = config["official_cases"]
    if report.get("passed") != count:
        raise SystemExit(f"Expected a full run of {count} cases; got {report.get('passed')} passes.")
    print(f"Official tests: {count}/{count} passed.", flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, help="solution file or directory; defaults to the bundled reference")
    parser.add_argument("--output", type=Path, help="new directory for reports; omit for a temporary run")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("The original resource checks require Windows.")
    config = json.loads((ROOT / "LOCK.json").read_text(encoding="utf-8"))
    candidate = args.candidate.resolve() if args.candidate else ROOT.parent / "reference"
    if args.output is not None:
        output = args.output.resolve()
        if output.exists():
            parser.error("The report directory must be a new path.")
        return run(candidate, output, config)

    with TemporaryDirectory(prefix="algorithm-eval-") as scratch:
        return run(candidate, Path(scratch) / "report", config)


if __name__ == "__main__":
    sys.exit(main())
