"""Rebuild snapshots from the longest valid journal prefix."""

import json
from pathlib import Path
import sys


def recover(folder):
    checkpoint = json.loads((folder / "checkpoint.json").read_bytes())
    values = checkpoint["items"]
    revision = checkpoint["revision"]
    pending = None
    for raw in (folder / "journal.jsonl").read_bytes().splitlines(keepends=True):
        if not raw.endswith(b"\n"):
            break
        try:
            record = json.loads(raw)
            op = record["op"]
            if op == "begin" and pending is None and record["revision"] == revision + 1:
                pending = values.copy()
            elif op == "set" and pending is not None:
                pending[record["key"]] = record["value"]
            elif op == "del" and pending is not None:
                pending.pop(record["key"], None)
            elif op == "commit" and pending is not None and record["revision"] == revision + 1:
                values = pending
                revision += 1
                pending = None
            else:
                break
        except (KeyError, TypeError, ValueError):
            break
    output = folder / "recovered.json"
    stage = output.with_suffix(".tmp")
    data = {"items": values, "revision": revision}
    stage.write_bytes((json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))+"\n").encode("utf-8"))
    stage.replace(output)


def main():
    jobs = Path(sys.argv[1])
    for name in jobs.read_text(encoding="ascii").splitlines():
        recover(jobs.parent / name)


if __name__ == "__main__":
    main()
