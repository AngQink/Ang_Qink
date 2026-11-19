"""Verifier helpers; the behavioral model uses copied states and a change log.

It deliberately does not import, execute, or share algorithms with the oracle.
"""
import ctypes
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import zlib

HEADER = b"CHRON1\r\n"


def c(op, tx="a", **fields):
    return dict(op=op, tx=tx, **fields)


def pack_frame(version, operations):
    payload = version.to_bytes(8, "little") + len(operations).to_bytes(4, "little")
    parts = [payload]
    for key, value in operations:
        raw_key = key.encode("utf-8")
        parts.extend([bytes([2 if value is None else 1]), len(raw_key).to_bytes(4, "little"), raw_key])
        if value is not None:
            raw_value = value.encode("utf-8")
            parts.extend([len(raw_value).to_bytes(4, "little"), raw_value])
    return wrap_payload(b"".join(parts))


def wrap_payload(payload):
    return len(payload).to_bytes(4, "little") + payload + (zlib.crc32(payload) & 0xffffffff).to_bytes(4, "little")


def inside(key, lo, hi):
    raw = key.encode("utf-8")
    return (lo is None or raw >= lo.encode("utf-8")) and (hi is None or raw < hi.encode("utf-8"))


class Model:
    def __init__(self):
        self.version = 0
        self.state = {}
        self.changed = []
        self.tx = {}
        self.expected_wal = HEADER

    def seed(self, writes):
        self.version += 1
        self._apply(writes)
        self.expected_wal += pack_frame(self.version, sorted(writes.items(), key=lambda i: i[0].encode("utf-8")))

    def _apply(self, writes):
        for key, value in writes.items():
            if value is None:
                self.state.pop(key, None)
            else:
                self.state[key] = value
        self.changed.append((self.version, set(writes)))

    def execute(self, command):
        op, name = command["op"], command["tx"]
        if op == "begin":
            self.tx[name] = {"at": self.version, "snapshot": dict(self.state), "writes": {},
                             "read": set(), "range": [], "save": []}
            return {"ok": True, "version": self.version}
        t = self.tx[name]
        writes = t["writes"]
        if op == "get":
            key = command["key"]
            t["read"].add(key)
            visible = dict(t["snapshot"])
            visible.update(writes)
            return {"value": visible.get(key)}
        if op == "scan":
            lo, hi = command["start"], command["end"]
            t["range"].append((lo, hi))
            visible = dict(t["snapshot"])
            visible.update(writes)
            return {"items": [[k, visible[k]] for k in sorted(visible, key=lambda k: k.encode("utf-8"))
                              if visible[k] is not None and inside(k, lo, hi)]}
        if op == "put":
            writes[command["key"]] = command["value"]
        elif op == "delete":
            writes[command["key"]] = None
        elif op == "savepoint":
            t["save"].append((command["name"], dict(writes)))
        elif op == "rollback":
            index = [label for label, _ in t["save"]].index(command["name"])
            t["writes"] = dict(t["save"][index][1])
            t["save"] = t["save"][:index + 1]
        elif op == "abort":
            del self.tx[name]
        elif op == "commit":
            del self.tx[name]
            watched = t["read"] | set(writes)
            for version, keys in self.changed:
                if version <= t["at"]:
                    continue
                if watched.intersection(keys) or any(inside(k, lo, hi)
                        for k in keys for lo, hi in t["range"]):
                    return {"ok": False, "error": "conflict"}
            if writes:
                self.seed(writes)
            return {"ok": True, "version": self.version}
        return {"ok": True}


def resident_bytes(process):
    if os.name == "nt":
        class Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [
                (name, ctypes.c_size_t) for name in (
                    "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                    "PagefileUsage", "PeakPagefileUsage", "PrivateUsage")]
        data = Counters()
        data.cb = ctypes.sizeof(data)
        api = ctypes.windll.psapi.GetProcessMemoryInfo
        api.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        api.restype = ctypes.c_int
        if api(int(process._handle), ctypes.byref(data), data.cb):
            return int(data.PeakWorkingSetSize)
    else:
        try:
            for line in Path(f"/proc/{process.pid}/status").read_text().splitlines():
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) * 1024
        except (FileNotFoundError, ProcessLookupError):
            pass
    return 0


class Runner:
    def __init__(self, candidate, workspace):
        self.candidate = Path(candidate)
        self.workspace = Path(workspace)
        self.serial = 0
        self.metrics = []

    def new_db(self, initial=None):
        self.serial += 1
        db = self.workspace / f"db-{self.serial:04d}"
        db.mkdir()
        if initial is not None:
            (db / "journal.wal").write_bytes(initial)
        return db

    def run(self, commands, db=None, timeout=15, launch=None):
        db = self.new_db() if db is None else db
        args = [sys.executable, str(self.candidate / "chronicle.py"), "--db", str(db)]
        if launch:
            args = launch + args[1:]
        started = time.perf_counter()
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                   cwd=self.candidate)
        done = threading.Event()
        peak = [0]
        exceeded = [False]

        def watch():
            while not done.wait(0.01):
                peak[0] = max(peak[0], resident_bytes(process))
                if peak[0] > 320 * 1024 * 1024:
                    exceeded[0] = True
                    process.kill()
                    return

        monitor = threading.Thread(target=watch, daemon=True)
        monitor.start()
        try:
            raw_input = "".join(json.dumps(cmd, ensure_ascii=False) + "\n" for cmd in commands)
            try:
                output, error = process.communicate(raw_input, timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                raise AssertionError(f"process exceeded {timeout}s")
        finally:
            done.set()
            monitor.join()
        elapsed = time.perf_counter() - started
        self.metrics.append({"elapsed_sec": round(elapsed, 4), "peak_working_set_mib": round(peak[0] / 2**20, 3)})
        assert not exceeded[0], f"database process exceeded 320 MiB (observed {peak[0] / 2**20:.1f} MiB)"
        assert process.returncode == 0, f"exit={process.returncode}; stderr={error[-2500:]}"
        try:
            lines = [json.loads(line) for line in output.splitlines()]
        except (ValueError, TypeError) as exc:
            raise AssertionError(f"invalid NDJSON output: {output[:500]!r}") from exc
        assert len(lines) == len(commands), f"expected {len(commands)} replies, got {len(lines)}"
        assert sorted(p.name for p in db.iterdir()) == ["journal.wal"], "unexpected persistent files"
        return lines, db

    def check(self, commands, model=None, db=None):
        model = Model() if model is None else model
        expected = [model.execute(cmd) for cmd in commands]
        actual, db = self.run(commands, db)
        for index, (want, got) in enumerate(zip(expected, actual)):
            assert got == want, f"command {index} {commands[index]!r}: expected {want!r}, got {got!r}"
        assert (db / "journal.wal").read_bytes() == model.expected_wal, "WAL differs from canonical committed frames"
        return model, db


class Session:
    def __init__(self, candidate, db):
        self.process = subprocess.Popen(
            [sys.executable, str(Path(candidate) / "chronicle.py"), "--db", str(db)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", cwd=candidate)
        self.queue = queue.Queue()

        def read():
            for line in self.process.stdout:
                self.queue.put(line)
            self.queue.put(None)

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def ask(self, command):
        self.process.stdin.write(json.dumps(command, ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        try:
            line = self.queue.get(timeout=5)
        except queue.Empty as exc:
            raise AssertionError("no immediate reply before EOF (5s)") from exc
        assert line is not None, "process closed stdout before replying"
        return json.loads(line)

    def kill(self):
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=5)
        self.reader.join(timeout=1)
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()
