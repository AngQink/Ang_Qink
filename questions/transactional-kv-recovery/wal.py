"""An early WAL implementation. See README.md for the actual contract."""
import struct
import zlib
from pathlib import Path

HEADER = b"CHRON1\r\n"
LIMIT = 8 * 1024 * 1024


def encode(version, writes):
    body = bytearray(struct.pack("<QI", version, len(writes)))
    for key, value in sorted(writes.items(), key=lambda item: item[0].encode("utf-8")):
        key_bytes = key.encode("utf-8")
        body += struct.pack("<BI", 2 if value is None else 1, len(key_bytes))
        body += key_bytes
        if value is not None:
            value_bytes = value.encode("utf-8")
            body += struct.pack("<I", len(value_bytes)) + value_bytes
    return struct.pack("<I", len(body)) + body + struct.pack("<I", zlib.crc32(body))


def decode(body):
    version, count = struct.unpack_from("<QI", body)
    offset = 12
    writes = {}
    for _ in range(count):
        tag, length = struct.unpack_from("<BI", body, offset)
        offset += 5
        key = body[offset:offset + length].decode("utf-8")
        offset += length
        value = None
        if tag == 1:
            length, = struct.unpack_from("<I", body, offset)
            offset += 4
            value = body[offset:offset + length].decode("utf-8")
            offset += length
        writes[key] = value
    return version, writes


class Journal:
    def __init__(self, directory):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        self.path = path / "journal.wal"
        if not self.path.exists() or not self.path.stat().st_size:
            self.path.write_bytes(HEADER)
        self.file = self.path.open("r+b")

    def recover(self):
        self.file.seek(len(HEADER))
        while length_bytes := self.file.read(4):
            if len(length_bytes) < 4:
                break
            length, = struct.unpack("<I", length_bytes)
            if length > LIMIT:
                break
            body = self.file.read(length)
            checksum = self.file.read(4)
            if len(body) != length or len(checksum) != 4:
                break
            try:
                yield decode(body)
            except (ValueError, struct.error):
                break
        self.file.seek(0, 2)

    def append(self, version, writes):
        self.file.write(encode(version, writes))
        self.file.flush()

    def close(self):
        self.file.close()
