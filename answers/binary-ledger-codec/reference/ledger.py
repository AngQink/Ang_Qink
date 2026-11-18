#!/usr/bin/env python3
"""Deterministic binary ledger implementation using the standard library."""
import bisect
import json
import os
import struct
import sys
import tempfile
import unicodedata

MAGIC = b"ASHLEDG1"
END_MAGIC = b"ASHEND01"
MAX_T = 1 << 53
NFC = unicodedata.normalize
U32 = struct.Struct("<I")
U64 = struct.Struct("<Q")
BLOCK = struct.Struct("<2sBHII")


def _crc_tables():
    table = []
    for n in range(256):
        for _ in range(8):
            n = (n >> 1) ^ (0x82F63B78 if n & 1 else 0)
        table.append(n)
    tables = [table]
    for _ in range(7):
        tables.append([(n >> 8) ^ table[n & 255] for n in tables[-1]])
    return tables


CRC_TABLES = _crc_tables()


def crc32c(data):
    view = memoryview(data)
    end = len(view) & ~7
    t0, t1, t2, t3, t4, t5, t6, t7 = CRC_TABLES
    crc = 0xffffffff
    if sys.byteorder == "little":
        for word in view[:end].cast("Q"):
            word ^= crc
            crc = (t7[word & 255] ^ t6[(word >> 8) & 255]
                   ^ t5[(word >> 16) & 255] ^ t4[(word >> 24) & 255]
                   ^ t3[(word >> 32) & 255] ^ t2[(word >> 40) & 255]
                   ^ t1[(word >> 48) & 255] ^ t0[word >> 56])
    else:
        end = 0
    for value in view[end:]:
        crc = (crc >> 8) ^ t0[(crc ^ value) & 255]
    return crc ^ 0xffffffff


class LedgerError(Exception):
    def __init__(self, code, offset):
        self.code, self.offset = code, offset
        super().__init__(code, offset)


class InputError(Exception):
    def __init__(self, line, code):
        self.line, self.code = line, code
        super().__init__(line, code)


def varint(value):
    out = bytearray()
    while value >= 128:
        out.append((value & 127) | 128)
        value >>= 7
    out.append(value)
    return bytes(out)


def read_varint(data, pos, end, bad, truncated, offset):
    value = 0
    for i in range(10):
        if pos >= end:
            raise LedgerError(truncated, offset)
        byte = data[pos]
        pos += 1
        # Malformation is decided at byte ten, even if it is also the final byte.
        if i == 9 and byte > 1:
            raise LedgerError(bad, offset)
        value |= (byte & 127) << (7 * i)
        if byte < 128:
            if i and byte == 0:
                raise LedgerError(bad, offset)
            return value, pos
    raise LedgerError(bad, offset)


def lz_encode(raw):
    size = len(raw)
    positions = {}
    indexed = pos = literal = 0
    out = bytearray()
    while pos < size:
        # Include every position, including positions inside earlier matches.
        until = min(pos, size - 3)
        for q in range(indexed, until):
            prefix = raw[q:q + 4]
            bucket = positions.get(prefix)
            if bucket is None:
                positions[prefix] = [q]
            else:
                bucket.append(q)
                if len(bucket) > 8:
                    del bucket[0]
        indexed = until
        best_length = best_q = 0
        if pos + 4 <= size:
            bucket = positions.get(raw[pos:pos + 4])
            if bucket:
                cap = min(65535, size - pos)
                for q in reversed(bucket):
                    if best_length:
                        if raw[q:q + best_length + 1] != raw[pos:pos + best_length + 1]:
                            continue
                        length = best_length + 1
                    else:
                        length = 4
                    # Compare long common runs in C before resolving the tail.
                    while (length + 256 <= cap and
                           raw[q + length:q + length + 256] == raw[pos + length:pos + length + 256]):
                        length += 256
                    while length < cap and raw[q + length] == raw[pos + length]:
                        length += 1
                    if length > best_length:
                        best_length, best_q = length, q
                    if best_length == cap:
                        break
        if best_length:
            if pos > literal:
                out.append(0)
                out.extend(varint(pos - literal))
                out.extend(raw[literal:pos])
            out.append(1)
            out.extend(varint(pos - best_q))
            out.extend(varint(best_length))
            pos += best_length
            literal = pos
        else:
            pos += 1
    if literal < size:
        out.append(0)
        out.extend(varint(size - literal))
        out.extend(raw[literal:])
    return bytes(out)


def lz_decode(stored, raw_len, block_offset):
    out = bytearray()
    pos, size = 0, len(stored)
    while True:
        have = len(out)
        if have == raw_len:
            if pos != size:
                raise LedgerError("BAD_LZ_TRAILING", block_offset)
            return bytes(out)
        if pos == size:
            raise LedgerError("BAD_LZ_TRUNCATED", block_offset)
        tag = stored[pos]
        pos += 1
        if tag == 0:
            length, pos = read_varint(stored, pos, size, "BAD_LZ_VARINT", "BAD_LZ_TRUNCATED", block_offset)
            if length < 1:
                raise LedgerError("BAD_LZ_LITERAL", block_offset)
            if have + length > raw_len:
                raise LedgerError("BAD_LZ_SIZE", block_offset)
            if length > size - pos:
                raise LedgerError("BAD_LZ_TRUNCATED", block_offset)
            out.extend(stored[pos:pos + length])
            pos += length
        elif tag == 1:
            distance, pos = read_varint(stored, pos, size, "BAD_LZ_VARINT", "BAD_LZ_TRUNCATED", block_offset)
            length, pos = read_varint(stored, pos, size, "BAD_LZ_VARINT", "BAD_LZ_TRUNCATED", block_offset)
            if distance < 1 or distance > have or length < 4:
                raise LedgerError("BAD_LZ_MATCH", block_offset)
            if have + length > raw_len:
                raise LedgerError("BAD_LZ_SIZE", block_offset)
            if length <= distance:
                out.extend(out[have - distance:have - distance + length])
            else:
                pattern = bytes(out[have - distance:])
                repeats, remainder = divmod(length, distance)
                out.extend(pattern * repeats)
                out.extend(pattern[:remainder])
        else:
            raise LedgerError("BAD_LZ_TOKEN", block_offset)


def decode_records(raw, count, block_offset, global_previous):
    records = []
    previous = b""
    pos, size = 0, len(raw)
    for _ in range(count):
        if size - pos < 2:
            raise LedgerError("RECORD_TRUNCATED", block_offset)
        shared, flags = raw[pos], raw[pos + 1]
        pos += 2
        suffix_len, pos = read_varint(raw, pos, size, "BAD_VARINT", "RECORD_TRUNCATED", block_offset)
        value_len, pos = read_varint(raw, pos, size, "BAD_VARINT", "RECORD_TRUNCATED", block_offset)
        timestamp, pos = read_varint(raw, pos, size, "BAD_VARINT", "RECORD_TRUNCATED", block_offset)
        suffix_end = pos + suffix_len
        record_end = suffix_end + (0 if flags & 1 else value_len)
        if record_end > size:
            raise LedgerError("RECORD_TRUNCATED", block_offset)
        if flags & 254 or (flags & 1 and value_len != 0):
            raise LedgerError("BAD_RECORD_FLAGS", block_offset)
        if shared > len(previous):
            raise LedgerError("BAD_SHARED", block_offset)
        key = previous[:shared] + raw[pos:suffix_end]
        try:
            key_text = key.decode("utf-8")
        except UnicodeError:
            raise LedgerError("BAD_KEY_UTF8", block_offset) from None
        if NFC("NFC", key_text) != key_text:
            raise LedgerError("BAD_KEY_NFC", block_offset)
        if len(key) > 4096:
            raise LedgerError("BAD_LIMIT", block_offset)
        if timestamp >= MAX_T:
            raise LedgerError("BAD_T", block_offset)
        value = None
        if not flags & 1:
            if value_len > 1048576:
                raise LedgerError("BAD_LIMIT", block_offset)
            value = raw[suffix_end:record_end]
            try:
                value.decode("utf-8")
            except UnicodeError:
                raise LedgerError("BAD_VALUE_UTF8", block_offset) from None
        if global_previous is not None and key <= global_previous:
            raise LedgerError("KEY_NOT_ASCENDING", block_offset)
        records.append((key, value, timestamp))
        previous = global_previous = key
        pos = record_end
    if pos != size:
        raise LedgerError("BAD_BLOCK_TAIL", block_offset)
    return records


def decode_block(data, start, boundary, previous):
    if start + 13 > boundary:
        raise LedgerError("BAD_BLOCK_TRUNCATED", start)
    magic, mode, count, raw_len, stored_len = BLOCK.unpack_from(data, start)
    if magic != b"BL":
        raise LedgerError("BAD_BLOCK_MAGIC", start)
    if mode > 1:
        raise LedgerError("BAD_BLOCK_MODE", start)
    if count == 0:
        raise LedgerError("BAD_BLOCK_RECORDS", start)
    if mode == 0 and stored_len != raw_len:
        raise LedgerError("BAD_BLOCK_SIZES", start)
    crc_offset = start + 13 + stored_len
    end = crc_offset + 4
    if end > boundary:
        raise LedgerError("BAD_BLOCK_TRUNCATED", start)
    if U32.unpack_from(data, crc_offset)[0] != crc32c(memoryview(data)[start:crc_offset]):
        raise LedgerError("BAD_BLOCK_CRC", crc_offset)
    raw = data[start + 13:crc_offset]
    if mode:
        raw = lz_decode(raw, raw_len, start)
    return decode_records(raw, count, start, previous), end


def check_header(data, recovery=False):
    if len(data) < 32:
        raise LedgerError("TRUNCATED_HEADER", len(data))
    if data[:8] != MAGIC:
        raise LedgerError("BAD_MAGIC", 0)
    if struct.unpack_from("<H", data, 8)[0] != 1:
        raise LedgerError("BAD_VERSION", 8)
    if recovery:
        return
    if struct.unpack_from("<H", data, 10)[0]:
        raise LedgerError("BAD_HEADER_FLAGS", 10)
    if U32.unpack_from(data, 12)[0]:
        raise LedgerError("BAD_RESERVED", 12)
    if U32.unpack_from(data, 28)[0] != crc32c(data[:28]):
        raise LedgerError("BAD_HEADER_CRC", 28)


def verify_data(data):
    check_header(data)
    size = len(data)
    if size < 56:
        raise LedgerError("TRUNCATED_FOOTER", size)
    footer = size - 24
    index_offset, index_len = struct.unpack_from("<QI", data, footer)
    if data[-8:] != END_MAGIC:
        raise LedgerError("BAD_FOOTER_MAGIC", size - 8)
    if U32.unpack_from(data, size - 12)[0] != crc32c(data[footer:footer + 12]):
        raise LedgerError("BAD_FOOTER_CRC", size - 12)
    if index_offset < 32 or index_len < 4 or index_offset + index_len != footer:
        raise LedgerError("BAD_INDEX_RANGE", footer)
    all_records, blocks = [], []
    cursor, previous = 32, None
    while cursor < index_offset:
        records, end = decode_block(data, cursor, index_offset, previous)
        blocks.append((records[0][0], cursor))
        all_records.extend(records)
        previous = records[-1][0]
        cursor = end
    if len(blocks) != U32.unpack_from(data, 24)[0]:
        raise LedgerError("BAD_BLOCK_COUNT", 24)
    if len(all_records) != U64.unpack_from(data, 16)[0]:
        raise LedgerError("BAD_RECORD_COUNT", 16)
    index_end = index_offset + index_len - 4
    pos = index_offset
    for first_key, block_offset in blocks:
        entry_start = pos
        length, pos = read_varint(data, pos, index_end, "BAD_INDEX_TRUNCATED", "BAD_INDEX_TRUNCATED", entry_start)
        if length + 8 > index_end - pos:
            raise LedgerError("BAD_INDEX_TRUNCATED", entry_start)
        key = data[pos:pos + length]
        pos += length
        offset = U64.unpack_from(data, pos)[0]
        pos += 8
        if key != first_key or offset != block_offset:
            raise LedgerError("BAD_INDEX_ENTRY", entry_start)
    if pos != index_end:
        raise LedgerError("BAD_INDEX_LEN", pos)
    if U32.unpack_from(data, index_end)[0] != crc32c(memoryview(data)[index_offset:index_end]):
        raise LedgerError("BAD_INDEX_CRC", index_end)
    return all_records, len(blocks)


def encode_record(record, previous):
    key, value, timestamp = record
    common = 0
    cap = min(255, len(previous), len(key))
    while common < cap and previous[common] == key[common]:
        common += 1
    suffix = key[common:]
    return (bytes((common, int(value is None))) + varint(len(suffix))
            + varint(0 if value is None else len(value)) + varint(timestamp)
            + suffix + (b"" if value is None else value))


def canonical_data(records):
    block_parts, index_parts = [], []
    offset = 32
    current = bytearray()
    count = 0
    first = None
    previous = b""

    def flush():
        nonlocal offset, current, count, first, previous
        if not count:
            return
        raw = bytes(current)
        tokens = lz_encode(raw)
        mode = int(len(tokens) < len(raw))
        payload = tokens if mode else raw
        body = BLOCK.pack(b"BL", mode, count, len(raw), len(payload)) + payload
        frame = body + U32.pack(crc32c(body))
        block_parts.append(frame)
        index_parts.append(varint(len(first)) + first + U64.pack(offset))
        offset += len(frame)
        current, count, first, previous = bytearray(), 0, None, b""

    for record in records:
        encoded = encode_record(record, previous)
        if count and len(current) + len(encoded) > 8192:
            flush()
            encoded = encode_record(record, b"")
        if not count:
            first = record[0]
        current.extend(encoded)
        count += 1
        previous = record[0]
    flush()
    header = struct.pack("<8sHHIQI", MAGIC, 1, 0, 0, len(records), len(block_parts))
    header += U32.pack(crc32c(header))
    index = b"".join(index_parts)
    index += U32.pack(crc32c(index))
    footer = struct.pack("<QI", offset, len(index))
    footer += U32.pack(crc32c(footer)) + END_MAGIC
    return header + b"".join(block_parts) + index + footer


def atomic_write(path, data):
    target = os.path.abspath(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=os.path.dirname(target),
                                         prefix=".ashen-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def read_file(path):
    with open(path, "rb") as stream:
        return stream.read()


def _invalid_constant(value):
    raise ValueError(value)


def read_input(data):
    winners = {}
    if not data:
        return []
    lines = data.split(b"\n")
    terminated = len(lines) - 1
    if lines[-1] == b"":
        lines.pop()
    for index, raw in enumerate(lines):
        line = index + 1
        if index < terminated and raw.endswith(b"\r"):
            raw = raw[:-1]
        try:
            item = json.loads(raw.decode("utf-8"), parse_constant=_invalid_constant)
        except (ValueError, UnicodeError, RecursionError):
            raise InputError(line, "INPUT_JSON") from None
        if not isinstance(item, dict):
            raise InputError(line, "INPUT_JSON")
        if (item.keys() != {"k", "v", "t"} or not isinstance(item["k"], str)
                or (item["v"] is not None and not isinstance(item["v"], str))
                or type(item["t"]) is not int):
            raise InputError(line, "INPUT_SCHEMA")
        try:
            key = NFC("NFC", item["k"]).encode("utf-8")
        except UnicodeError:
            raise InputError(line, "INPUT_KEY") from None
        if len(key) > 4096:
            raise InputError(line, "INPUT_KEY")
        try:
            value = None if item["v"] is None else item["v"].encode("utf-8")
        except UnicodeError:
            raise InputError(line, "INPUT_VALUE") from None
        if value is not None and len(value) > 1048576:
            raise InputError(line, "INPUT_VALUE")
        timestamp = item["t"]
        if not 0 <= timestamp < MAX_T:
            raise InputError(line, "INPUT_T")
        old = winners.get(key)
        if old is None or timestamp >= old[2]:
            winners[key] = (key, value, timestamp)
    return [winners[key] for key in sorted(winners)]


def emit(text):
    sys.stdout.buffer.write(text.encode("utf-8"))


def parse_scan(args):
    if not args or args[0].startswith("--"):
        raise ValueError("usage")
    start = limit = None
    seen = set()
    pos = 1
    while pos < len(args):
        flag = args[pos]
        if flag not in ("--from", "--limit") or flag in seen or pos + 1 >= len(args):
            raise ValueError("usage")
        seen.add(flag)
        value = args[pos + 1]
        if flag == "--from":
            start = NFC("NFC", value).encode("utf-8")
        else:
            if not value or any(ch < "0" or ch > "9" for ch in value):
                raise ValueError("usage")
            limit = int(value)
        pos += 2
    return start, limit


def main(argv=None):
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        emit("ERR USAGE\n")
        return 3
    command, args = argv[0], argv[1:]
    valid = ((command in ("build", "recover") and len(args) == 2)
             or (command in ("info", "verify") and len(args) == 1)
             or (command in ("get", "merge") and len(args) >= 2)
             or (command == "scan" and len(args) >= 1))
    if not valid:
        emit("ERR USAGE\n")
        return 3
    if command == "scan":
        try:
            start, limit = parse_scan(args)
        except (ValueError, UnicodeError):
            emit("ERR USAGE\n")
            return 3
    try:
        if command == "build":
            records = read_input(read_file(args[0]))
            atomic_write(args[1], canonical_data(records))
        elif command == "merge":
            winners = {}
            for path in args[1:]:
                records, _ = verify_data(read_file(path))
                for record in records:
                    old = winners.get(record[0])
                    if old is None or record[2] >= old[2]:
                        winners[record[0]] = record
            records = [winners[key] for key in sorted(winners)]
            atomic_write(args[0], canonical_data(records))
        elif command == "recover":
            data = read_file(args[0])
            check_header(data, recovery=True)
            records = []
            pos, previous = 32, None
            while pos < len(data):
                try:
                    block_records, end = decode_block(data, pos, len(data), previous)
                except LedgerError:
                    break
                records.extend(block_records)
                previous = block_records[-1][0]
                pos = end
            atomic_write(args[1], canonical_data(records))
            emit(f"RECOVERED {len(records)}\n")
        else:
            data = read_file(args[0])
            records, blocks = verify_data(data)
            if command == "verify":
                emit(f"OK {len(records)} {blocks}\n")
            elif command == "info":
                emit(json.dumps({"records": len(records), "blocks": blocks, "bytes": len(data)}) + "\n")
            elif command == "get":
                values = {key: value for key, value, _ in records}
                for key in args[1:]:
                    value = values.get(NFC("NFC", key).encode("utf-8"))
                    emit(json.dumps(None if value is None else value.decode("utf-8"), ensure_ascii=False) + "\n")
            elif command == "scan":
                first = 0 if start is None else bisect.bisect_left(records, start, key=lambda record: record[0])
                end = len(records) if limit is None else min(len(records), first + limit)
                for index in range(first, end):
                    key, value, timestamp = records[index]
                    emit(json.dumps({"k": key.decode("utf-8"),
                                     "v": None if value is None else value.decode("utf-8"),
                                     "t": timestamp}, ensure_ascii=False) + "\n")
        return 0
    except InputError as error:
        emit(f"ERR INPUT {error.line} {error.code}\n")
        return 4
    except LedgerError as error:
        emit(f"ERR {error.code} {error.offset}\n")
        return 1 if command == "verify" else 2
    except OSError:
        emit("ERR IO\n")
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
