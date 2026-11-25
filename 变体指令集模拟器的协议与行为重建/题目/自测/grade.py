from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copyfile
import argparse
import json
import subprocess
import sys


HERE = Path(__file__).resolve().parents[1]
ENTRY = 'ghost.py'


def run(candidate: Path):
    cases = sorted(p.parent for p in (HERE / "samples").glob("*/input.bin"))
    if not cases:
        raise ValueError("The original samples directory is empty.")
    passed = 0
    with TemporaryDirectory(prefix="deepseek-sample-") as temp:
        isolated = Path(temp) / ENTRY
        copyfile(candidate, isolated)
        for case in cases:
            expected_code = (int((case / "expected_exit.txt").read_text(encoding="ascii"))
                             if (case / "expected_exit.txt").is_file()
                             else json.loads((case / "meta.json").read_bytes())["exit"])
            fields = ((case / "expected_stdout.bin").read_bytes(),
                      (case / "expected_stderr.bin").read_bytes(), expected_code)
            try:
                got = subprocess.run([sys.executable, "-B", "-I", str(isolated)], cwd=temp,
                                     input=(case / "input.bin").read_bytes(), capture_output=True,
                                     timeout=60, check=False)
            except subprocess.TimeoutExpired:
                print(f"FAIL {case.name}: timeout")
                continue
            actual = got.stdout, got.stderr, got.returncode
            if fields == actual:
                print(f"PASS {case.name}")
                passed += 1
            else:
                changed = ", ".join(k for k, a, b in zip(("stdout", "stderr", "exit code"), actual, fields)
                                    if a != b)
                print(f"FAIL {case.name}: {changed}")
    print(f"{passed}/{len(cases)} original public samples")
    return passed == len(cases)


def main():
    parser = argparse.ArgumentParser(description="Replay the archived public samples byte for byte.")
    parser.add_argument("--candidate", type=Path, default=HERE / "workspace",
                        help=f"Path to {ENTRY} or the directory containing it.")
    args = parser.parse_args()
    source = args.candidate.resolve()
    if source.is_dir():
        source /= ENTRY
    if not source.is_file():
        parser.error(f"Expected a Python submission at {source}")
    return 0 if run(source) else 1


if __name__ == "__main__":
    sys.exit(main())
