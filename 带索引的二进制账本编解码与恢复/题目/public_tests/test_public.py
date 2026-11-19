"""Public format and command-line tests for the indexed binary ledger."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

WS = Path(__file__).resolve().parents[1]
LEDGER = WS / "ledger.py"
SAMPLES = WS / "samples"

BUILD_SAMPLES = ["01_empty", "03_unicode"]


def run(*args, expect=0):
    proc = subprocess.run(
        [sys.executable, str(LEDGER), *args],
        cwd=str(WS),
        capture_output=True,
    )
    assert proc.returncode == expect, (
        f"expected exit {expect}, got {proc.returncode}\n"
        f"stdout={proc.stdout!r}\nstderr={proc.stderr!r}"
    )
    return proc


@pytest.mark.parametrize("name", BUILD_SAMPLES)
def test_build_matches_sample(name, tmp_path):
    src = SAMPLES / name / "input.ndjson"
    expected = (SAMPLES / name / "expected.algr").read_bytes()
    out = tmp_path / "out.algr"
    run("build", str(src), str(out))
    assert out.read_bytes() == expected


@pytest.mark.parametrize("name", ["03_unicode"])
def test_scan_matches_sample(name):
    expected = (SAMPLES / name / "expected_scan.txt").read_bytes()
    proc = run("scan", str(SAMPLES / name / "expected.algr"))
    assert proc.stdout == expected


def test_verify_ok():
    proc = run("verify", str(SAMPLES / "03_unicode" / "expected.algr"))
    assert proc.stdout.startswith(b"OK ")


def test_verify_bad_magic(tmp_path):
    bad = tmp_path / "bad.algr"
    bad.write_bytes(b"\x00" * 100)
    proc = run("verify", str(bad), expect=1)
    assert proc.stdout == b"ERR BAD_MAGIC 0\n"


def test_get_missing_key():
    proc = run("get", str(SAMPLES / "03_unicode" / "expected.algr"), "__missing_key__")
    assert proc.stdout == b"null\n"


def test_info_fields():
    path = SAMPLES / "03_unicode" / "expected.algr"
    proc = run("info", str(path))
    data = json.loads(proc.stdout.decode("utf-8"))
    assert set(data) == {"records", "blocks", "bytes"}
    assert data["bytes"] == path.stat().st_size


def test_recover_torn(tmp_path):
    src_dir = SAMPLES / "06_torn"
    expected = (src_dir / "expected_recovered.algr").read_bytes()
    expected_count = (src_dir / "expected_recovered_count.txt").read_text()
    out = tmp_path / "rec.algr"
    proc = run("recover", str(src_dir / "torn.algr"), str(out))
    assert out.read_bytes() == expected
    assert proc.stdout == f"RECOVERED {expected_count.strip()}".encode() + b"\n"


def test_usage_error():
    proc = subprocess.run([sys.executable, str(LEDGER)], cwd=str(WS), capture_output=True)
    assert proc.returncode == 3
    assert proc.stdout == b"ERR USAGE\n"
