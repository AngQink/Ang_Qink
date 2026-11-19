import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(db, commands):
    result = subprocess.run(
        [sys.executable, str(ROOT / "chronicle.py"), "--db", str(db)],
        input="".join(json.dumps(c, ensure_ascii=False) + "\n" for c in commands),
        text=True, encoding="utf-8", capture_output=True, timeout=10, cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    return [json.loads(line) for line in result.stdout.splitlines()]


def c(op, tx="a", **kw):
    return dict(op=op, tx=tx, **kw)


def test_basic_and_restart(tmp_path):
    assert run(tmp_path, [c("begin"), c("put", key="药", value=""), c("commit")])[-1] == {
        "ok": True, "version": 1}
    assert run(tmp_path, [c("begin"), c("get", key="药")])[-1] == {"value": ""}


def test_snapshot_is_stable(tmp_path):
    result = run(tmp_path, [c("begin"), c("begin", "b"),
                           c("put", "b", key="k", value="new"), c("commit", "b"),
                           c("get", key="k")])
    assert result[-1] == {"value": None}


def test_empty_scan_tracks_phantoms(tmp_path):
    result = run(tmp_path, [c("begin"), c("scan", start="m", end="n"),
                           c("begin", "b"), c("put", "b", key="moon", value="1"),
                           c("commit", "b"), c("commit")])
    assert result[-1] == {"ok": False, "error": "conflict"}


def test_rollback_keeps_read_dependency(tmp_path):
    result = run(tmp_path, [c("begin"), c("savepoint", name="s"), c("get", key="ghost"),
                           c("rollback", name="s"), c("begin", "b"),
                           c("delete", "b", key="ghost"), c("commit", "b"), c("commit")])
    assert result[-1] == {"ok": False, "error": "conflict"}


def test_torn_tail_is_removed_before_append(tmp_path):
    run(tmp_path, [c("begin"), c("put", key="a", value="1"), c("commit")])
    wal = tmp_path / "journal.wal"
    prefix = wal.read_bytes()
    wal.write_bytes(prefix + b"\x20\x00")
    run(tmp_path, [c("begin"), c("put", key="b", value="2"), c("commit")])
    assert run(tmp_path, [c("begin"), c("get", key="b")])[-1] == {"value": "2"}
    assert wal.read_bytes().startswith(prefix)
