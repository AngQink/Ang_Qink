"""Offline binary verifier. Only copied candidate .py files are evaluated."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time
import traceback

from cases import CASES
from support import Runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--group", help="diagnostic subset; not an official full result")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    source = Path(args.candidate).resolve(strict=True)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "reward.txt").write_text("0\n", encoding="ascii")
    scratch = Path(tempfile.mkdtemp(prefix="scratch-", dir=out))
    records = []
    report = {"candidate": str(source), "reward": 0, "complete_suite": not bool(args.group),
              "cases": records, "source_sha256": {}}
    try:
        player = scratch / "candidate"
        player.mkdir()
        for path in sorted(source.rglob("*.py")):
            relative = path.relative_to(source)
            if any(part in ("public_tests", "__pycache__", ".venv") for part in relative.parts):
                continue
            if path.is_symlink() or any(p.is_symlink() or p.is_junction() for p in [path, *path.parents] if p != p.parent):
                raise ValueError(f"reparse/symlink candidate file is not supported: {relative}")
            target = player / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = path.read_bytes()
            target.write_bytes(raw)
            report["source_sha256"][relative.as_posix()] = hashlib.sha256(raw).hexdigest()
        assert (player / "chronicle.py").is_file(), "missing chronicle.py"
        runner = Runner(player, scratch)
        selected = [entry for entry in CASES if not args.group or entry[0] == args.group]
        assert selected, "no matching cases"
        for group, name, fn in selected:
            started = time.perf_counter()
            prior = len(runner.metrics)
            try:
                fn(runner)
                status, error = "PASS", None
            except Exception as exc:
                status = "FAIL"
                error = f"{type(exc).__name__}: {exc}"[:4000]
            record = {"group": group, "name": name, "status": status,
                      "elapsed_sec": round(time.perf_counter() - started, 4),
                      "processes": runner.metrics[prior:]}
            if error:
                record["error"] = error
            records.append(record)
            print(f"{status:4}  {group:12} {name}" + (f" -- {error[:180]}" if error else ""), flush=True)
        count = Counter(record["status"] for record in records)
        report["passed"] = count["PASS"]
        report["total"] = len(records)
        report["reward"] = int(not args.group and bool(records) and count["FAIL"] == 0)
        print(f"\n{count['PASS']}/{len(records)} passed; reward={report['reward']}")
    except Exception as exc:
        report["infrastructure_error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    finally:
        (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "reward.txt").write_text(str(report["reward"]) + "\n", encoding="ascii")
        # Delete only this run's mkdtemp directory, after checking scope and links.
        assert scratch.resolve().parent == out.resolve() and scratch.name.startswith("scratch-")
        entries = [scratch, *scratch.rglob("*")]
        if any(p.is_symlink() or p.is_junction() for p in entries):
            print(f"Retaining scratch containing links: {scratch}", file=sys.stderr)
        else:
            shutil.rmtree(scratch)
    return 0 if report["reward"] == 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
