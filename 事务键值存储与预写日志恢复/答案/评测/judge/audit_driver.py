"""Observe actual fsync of the WAL and publication order in a subprocess."""
import json
import os
from pathlib import Path
import runpy
import sys

trace = Path(sys.argv[1])
script = Path(sys.argv[2])
sys.argv = sys.argv[2:]
sys.path.insert(0, str(script.parent))
db = Path(sys.argv[sys.argv.index("--db") + 1])
real_fsync = os.fsync
real_stdout = sys.stdout


def event(value):
    with trace.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def fsync(fd):
    result = real_fsync(fd)
    wal = db / "journal.wal"
    if wal.exists():
        target, actual = wal.stat(), os.fstat(fd)
        if (target.st_dev, target.st_ino) == (actual.st_dev, actual.st_ino):
            event({"sync": target.st_size})
    return result


class Output:
    def __init__(self):
        self.pending = ""

    def reconfigure(self, **kw):
        return real_stdout.reconfigure(**kw)

    def write(self, value):
        self.pending += value
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            event({"output": json.loads(line)})
        return real_stdout.write(value)

    def flush(self):
        return real_stdout.flush()

    def __getattr__(self, name):
        return getattr(real_stdout, name)


os.fsync = fsync
sys.stdout = Output()
runpy.run_path(str(script), run_name="__main__")
