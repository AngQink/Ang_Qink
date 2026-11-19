"""Private reference implementation. Do not include in the player bundle."""
import argparse
import bisect
import json
import os
from pathlib import Path
import struct
import sys
import zlib

HEADER = b"CHRON1\r\n"
LIMIT = 8 * 1024 * 1024


def encode(version, writes):
    body = bytearray(struct.pack("<QI", version, len(writes)))
    for key, value in sorted(writes.items(), key=lambda item: item[0].encode("utf-8")):
        raw = key.encode("utf-8")
        body += struct.pack("<BI", 2 if value is None else 1, len(raw)) + raw
        if value is not None:
            raw = value.encode("utf-8")
            body += struct.pack("<I", len(raw)) + raw
    if not 12 <= len(body) <= LIMIT:
        raise ValueError("frame too large")
    return struct.pack("<I", len(body)) + body + struct.pack("<I", zlib.crc32(body) & 0xffffffff)


def decode(body, expected_version):
    offset = 0

    def take(size):
        nonlocal offset
        if size > len(body) - offset:
            raise ValueError("truncated payload field")
        raw = body[offset:offset + size]
        offset += size
        return raw

    def uint32():
        return struct.unpack("<I", take(4))[0]

    version = struct.unpack("<Q", take(8))[0]
    count = uint32()
    if version != expected_version or count == 0:
        raise ValueError("version/count")
    writes = {}
    previous = None
    for _ in range(count):
        tag = take(1)[0]
        if tag not in (1, 2):
            raise ValueError("tag")
        raw_key = take(uint32())
        if previous is not None and raw_key <= previous:
            raise ValueError("key order")
        previous = raw_key
        key = raw_key.decode("utf-8", errors="strict")
        value = take(uint32()).decode("utf-8", errors="strict") if tag == 1 else None
        writes[key] = value
    if offset != len(body):
        raise ValueError("unused payload bytes")
    return version, writes


class Journal:
    def __init__(self, directory):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        self.path = path / "journal.wal"
        if not self.path.exists() or self.path.stat().st_size == 0:
            with self.path.open("wb") as stream:
                stream.write(HEADER)
                stream.flush()
                os.fsync(stream.fileno())
        self.file = self.path.open("r+b")

    def recover(self):
        stream = self.file
        stream.seek(len(HEADER))
        good_end = len(HEADER)
        expected = 1
        while True:
            raw_length = stream.read(4)
            if not raw_length:
                break
            if len(raw_length) != 4:
                break
            length = struct.unpack("<I", raw_length)[0]
            if not 12 <= length <= LIMIT:
                break
            body = stream.read(length)
            checksum = stream.read(4)
            if len(body) != length or len(checksum) != 4:
                break
            if struct.unpack("<I", checksum)[0] != zlib.crc32(body) & 0xffffffff:
                break
            try:
                result = decode(body, expected)
            except (ValueError, struct.error, UnicodeError):
                break
            good_end = stream.tell()
            expected += 1
            yield result
        stream.seek(0, os.SEEK_END)
        if stream.tell() != good_end:
            stream.truncate(good_end)
            stream.flush()
            os.fsync(stream.fileno())
        stream.seek(good_end)

    def append(self, version, writes):
        self.file.write(encode(version, writes))
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self):
        self.file.close()


class Engine:
    def __init__(self, directory):
        self.journal = Journal(directory)
        self.version = 0
        self.histories = {}
        self.keys = []
        self.transactions = {}
        for version, writes in self.journal.recover():
            self._publish(version, writes)

    def _publish(self, version, writes):
        for key, value in writes.items():
            history = self.histories.get(key)
            if history is None:
                self.histories[key] = history = []
                bisect.insort(self.keys, key)
            history.append((version, value))
        self.version = version

    def _at(self, key, snapshot):
        history = self.histories.get(key, [])
        index = bisect.bisect_right(history, (snapshot + 1,)) - 1
        return history[index][1] if index >= 0 else None

    def _changed(self, key, since):
        history = self.histories.get(key)
        return history is not None and history[-1][0] > since

    def _conflict(self, tx):
        since = tx["version"]
        if any(self._changed(k, since) for k in tx["writes"].keys() | tx["reads"]):
            return True
        for lo, hi in tx["ranges"]:
            start = 0 if lo is None else bisect.bisect_left(self.keys, lo)
            end = len(self.keys) if hi is None else bisect.bisect_left(self.keys, hi)
            if any(self._changed(self.keys[index], since) for index in range(start, end)):
                return True
        return False

    def execute(self, command):
        op, name = command["op"], command["tx"]
        if op == "begin":
            self.transactions[name] = {
                "version": self.version, "writes": {}, "reads": set(),
                "ranges": [], "savepoints": [],
            }
            return {"ok": True, "version": self.version}
        tx = self.transactions[name]
        writes = tx["writes"]
        if op == "get":
            key = command["key"]
            tx["reads"].add(key)
            return {"value": writes[key] if key in writes else self._at(key, tx["version"])}
        if op == "scan":
            lo, hi = command["start"], command["end"]
            tx["ranges"].append((lo, hi))
            start = 0 if lo is None else bisect.bisect_left(self.keys, lo)
            end = len(self.keys) if hi is None else bisect.bisect_left(self.keys, hi)
            candidates = set(self.keys[start:end])
            candidates.update(k for k in writes if (lo is None or lo <= k) and (hi is None or k < hi))
            items = []
            for key in sorted(candidates):
                value = writes[key] if key in writes else self._at(key, tx["version"])
                if value is not None:
                    items.append([key, value])
            return {"items": items}
        if op in ("put", "delete"):
            writes[command["key"]] = command["value"] if op == "put" else None
        elif op == "savepoint":
            tx["savepoints"].append((command["name"], writes.copy()))
        elif op == "rollback":
            for index in range(len(tx["savepoints"]) - 1, -1, -1):
                label, saved = tx["savepoints"][index]
                if label == command["name"]:
                    tx["writes"] = saved.copy()
                    del tx["savepoints"][index + 1:]
                    break
        elif op == "abort":
            del self.transactions[name]
        elif op == "commit":
            del self.transactions[name]
            if self._conflict(tx):
                return {"ok": False, "error": "conflict"}
            if writes:
                version = self.version + 1
                self.journal.append(version, writes)
                self._publish(version, writes)
            return {"ok": True, "version": self.version}
        return {"ok": True}

    def close(self):
        self.journal.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    engine = Engine(args.db)
    try:
        for line in sys.stdin:
            print(json.dumps(engine.execute(json.loads(line)), ensure_ascii=False,
                             separators=(",", ":")), flush=True)
    finally:
        engine.close()


if __name__ == "__main__":
    main()
