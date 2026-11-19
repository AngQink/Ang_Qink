# 带索引的二进制账本编解码与恢复 / Encoding and Recovery of an Indexed Binary Ledger

**Status: normative.** A requirement marked "must" is mandatory. The canonical form is the
byte sequence that `build`, `merge` and `recover` must produce.

---

## 0. Deliverable, environment, determinism

1. Implement a **single, self-contained file** `ledger.py` at the root of this workspace.
2. Run it with `python ledger.py <command> ...` (CPython 3.14).
   Use the **Python standard library only**. No third-party packages, no compiled extensions.
3. `ledger.py` must work when it is the only file copied into an empty directory and executed there
   (it may not read sibling data files, its own source aside).
4. All text written to stdout must be encoded as **UTF-8 bytes**, regardless of the Windows console code
   page, locale, or `PYTHONIOENCODING`. Use `\n` (0x0A) as the line separator, never `\r\n`.
   All input files (`*.ndjson` and ledger files) are byte streams; `.ndjson` is UTF-8.
5. Output must be deterministic: identical inputs produce identical bytes and identical stdout.
6. No network access, no subprocesses. Do not rely on the current directory or environment.

The challenge includes `samples/` (input and expected output), `public_tests/` (basic format and
CLI checks), and a `ledger.py` starter.

---

## 1. Primitive encodings

### 1.1 Fixed-width integers

All fixed-width integers are **unsigned little-endian**:
`u8`, `u16`, `u32`, `u64`. There are no signed fixed-width integers.

### 1.2 `varint` — unsigned LEB128

Encode a non-negative integer `v` (0 ≤ v < 2^64) in base-128, least significant 7-bit group first; each
byte carries 7 payload bits in bits 0–6 and a continuation bit in bit 7. The encoding is **canonical**:
the shortest encoding must be used. A multi-byte encoding must therefore not end in `0x00`.
Examples: `0` → `00`, `127` → `7F`, `128` → `80 01`, `300` → `AC 02`.

A decoder must reject: encodings longer than 10 bytes, encodings whose value exceeds 2^64−1, and
non-canonical encodings (e.g. `80 00`, `81 00`). Any such failure is the error `BAD_VARINT` at the offset
defined by the surrounding structure (see §8), except where a later section maps it to a more specific
code (`BAD_LZ_VARINT` inside an LZ token stream, `BAD_INDEX_TRUNCATED` for index varints).

### 1.3 CRC-32C

`crc32c(data)` is the standard **CRC-32C (Castagnoli)** checksum: reflected input/output,
polynomial 0x1EDC6F41 (reflected form 0x82F63B78), initial value 0xFFFFFFFF, final XOR 0xFFFFFFFF.
Sanity check: `crc32c(b"123456789") == 0xE3069283`. `crc32c(b"") == 0x00000000`.
All CRC fields in this format are the 32-bit little-endian encoding of such a value.

### 1.4 Text

- **Keys** are Unicode strings. Before use a key is normalized to Unicode **NFC** (UAX #15);
  every operation (build, merge, get, scan filters, ordering, duplicate detection) uses the NFC form.
- **Values** are Unicode strings and are stored **without** normalization.
- In the file, keys and values are stored as their **UTF-8 byte sequences**.
- A key's byte length is measured **after** NFC normalization.
- Empty keys (`""`) and empty values (`""`) are legal. A value of JSON `null` means *tombstone* (see §4.2).

---

## 2. File layout

An `.algr` file is exactly:

```
+--------------------------------+ offset 0
| Header            32 bytes     |
+--------------------------------+ offset 32
| Block 0                        |   zero or more blocks, back to back
| Block 1                        |
| ...                            |
+--------------------------------+ index_offset
| Index entries                  |   one entry per block
| index_crc         4 bytes      |
+--------------------------------+ index_offset + index_len  (= file_size - 24)
| Footer            24 bytes     |
+--------------------------------+ file_size
```

`file_size = index_offset + index_len + 24`. There are no bytes between the last block and
`index_offset`, and no bytes after the footer. `index_len = len(index entries) + 4`.

---

## 3. Header (32 bytes, offset 0)

| offset | size | field          | value / meaning |
|-------:|-----:|----------------|-----------------|
| 0      | 8    | `magic`        | the 8 bytes `41 53 48 4C 45 44 47 31` (`"ASHLEDG1"`) |
| 8      | 2    | `version`      | `u16` = 1 |
| 10     | 2    | `header_flags` | `u16` = 0 |
| 12     | 4    | `reserved`     | `u32` = 0 |
| 16     | 8    | `record_count` | `u64`, total number of records in all blocks |
| 24     | 4    | `block_count`  | `u32`, total number of blocks |
| 28     | 4    | `header_crc`   | `u32` = `crc32c(bytes[0:28])` |

---

## 4. Blocks

Blocks are concatenated immediately after the header, starting at offset 32.

### 4.1 Block framing

A block at file offset `B`:

| offset | size | field          | value / meaning |
|-------:|-----:|----------------|-----------------|
| +0     | 2    | `block_magic`  | bytes `42 4C` (`"BL"`) |
| +2     | 1    | `mode`         | 0 = stored, 1 = LZ-compressed |
| +3     | 2    | `records`      | `u16`, number of records in this block, must be ≥ 1 |
| +5     | 4    | `raw_len`      | `u32`, length of the uncompressed record stream in bytes |
| +9     | 4    | `stored_len`   | `u32`, length of `stored_payload` |
| +13    | `stored_len` | `stored_payload` | if `mode==0`: the record stream itself; if `mode==1`: an LZ token stream |
| +13+`stored_len` | 4 | `block_crc` | `u32` = `crc32c(block bytes [B, B+13+stored_len))` |

Block total length = `17 + stored_len`; blocks are contiguous and in ascending key order.
Limits: `raw_len`, `stored_len` are `u32`; `records` fits in `u16`.
A block with `mode == 0` must have `stored_len == raw_len`.

### 4.2 Record stream (the uncompressed payload)

The uncompressed payload of a block is the concatenation, in key order, of encoded records:

```
record := shared   u8
          flags    u8
          suffix_len  varint
          value_len   varint
          t           varint
          suffix      suffix_len bytes
          value       value_len bytes, present iff flags bit 0 == 0
```

- `flags`: bit 0 = tombstone. Bits 1–7 must be 0.
  - If bit 0 is set (tombstone), `value_len` **must** be 0 and no value bytes follow.
  - If bit 0 is clear, `value_len` may be 0 (empty value) and exactly `value_len` value bytes follow.
- `shared` is the length of the common byte prefix with the **previous record's key bytes in the same
  block**, capped at 255. The first record of a block **must** have `shared == 0`.
  In every record `shared <= len(previous key bytes)`; a record's key bytes are
  `previous key bytes[0:shared] + suffix`, and for the first record of a block they are just `suffix`.
- `suffix_len = len(suffix)`, `value_len = len(value bytes)`, `t` = record timestamp.
- The decoded key (as a byte string) must be valid UTF-8, must equal its own NFC normalization,
  and must be ≤ 4096 bytes long. The value must be valid UTF-8 and ≤ 1048576 bytes long.
  `t` must satisfy `0 <= t < 2^53`.
- Keys are strictly ascending in unsigned lexicographic byte order over the whole file
  (not merely within a block); two equal keys are forbidden. `""` is a legal key and sorts first.
- The payload must contain exactly `records` complete records and consume `raw_len` bytes exactly;
  trailing bytes inside the decompressed payload are an error.

Empty values are encoded with `value_len = 0` and no bytes; tombstones likewise but with flags bit 0 set.

Decoding order for one record (this is also the order in which record-level errors are reported):

1. The `shared` and `flags` bytes must be present, else `RECORD_TRUNCATED`.
2. Decode `suffix_len`, `value_len`, `t` varints in that order. If the payload ends inside a varint →
   `RECORD_TRUNCATED`; if a varint is non-canonical or larger than `u64` → `BAD_VARINT`.
3. Truncation of the variable-length bytes: if flags bit 0 is clear, `suffix_len + value_len` bytes must be
   present; if it is set, only `suffix_len` bytes must be present. Missing bytes → `RECORD_TRUNCATED`.
4. Flags validity: bits 1–7 set → `BAD_RECORD_FLAGS`; bit 0 set and `value_len != 0` → `BAD_RECORD_FLAGS`.
5. `shared > len(previous key bytes)` → `BAD_SHARED` (this also enforces `shared == 0` for the first record
   of every block).
6. key bytes = `previous key bytes[0:shared] + suffix`; invalid UTF-8 → `BAD_KEY_UTF8`; not equal to its own
   NFC normalization → `BAD_KEY_NFC`; longer than 4096 bytes → `BAD_LIMIT`.
7. `t >= 2^53` → `BAD_T`.
8. For a non-tombstone: `value_len > 1048576` → `BAD_LIMIT`; invalid UTF-8 value → `BAD_VALUE_UTF8`.
9. The key bytes must be greater than the previous record's key bytes (previous record in the block, or —
   for the first record of a block — the last record of the previous block) → `KEY_NOT_ASCENDING`.

### 4.3 LZ token stream (`mode == 1`)

`stored_payload` is a token stream that expands to the record stream:

```
token := 0x00  varint(literal_len)  literal_len bytes      # literal run, literal_len >= 1
       | 0x01  varint(offset)  varint(match_len)           # back-reference, match_len >= 4
```

Decoding algorithm, with checks in exactly this order:

1. If the output is already exactly `raw_len` bytes long: stop. If any stored bytes remain →
   `BAD_LZ_TRAILING`.
2. If no stored bytes remain while the output is still shorter than `raw_len` → `BAD_LZ_TRUNCATED`.
3. Read one token byte and advance.
4. Token `0x00`: read `literal_len` as a varint (stored bytes run out → `BAD_LZ_TRUNCATED`; non-canonical or
   oversized varint → `BAD_LZ_VARINT`). Then, in this order: `literal_len < 1` → `BAD_LZ_LITERAL`;
   `len(output) + literal_len > raw_len` → `BAD_LZ_SIZE`; fewer than `literal_len` stored bytes remain →
   `BAD_LZ_TRUNCATED`. Append the literal bytes.
5. Token `0x01`: read `offset`, then `match_len`, each as a varint with the same varint error mapping as in
   step 4. Then, in this order: `offset < 1` or `offset > len(output)` → `BAD_LZ_MATCH`;
   `match_len < 4` → `BAD_LZ_MATCH`; `len(output) + match_len > raw_len` → `BAD_LZ_SIZE`.
   Then copy `match_len` bytes starting `offset` bytes back in the output, byte by byte; overlapping is
   allowed.
6. Any other token byte → `BAD_LZ_TOKEN`.

Repeat from step 1.

### 4.4 Canonical LZ encoder (`mode == 1` bytes produced by `build`/`merge`/`recover`)

Let `R` be the uncompressed record stream (`N = len(R)`). The canonical encoder is exactly:

```
out = bytearray(); pos = 0; lit_start = 0
# candidate index: for every 4-byte prefix, remember the most recent positions where it occurs.
# Before searching at position pos, the candidate lists contain every q < pos with q+4 <= N.
while pos < N:
    best = none
    if pos + 4 <= N:
        qs = positions q with q < pos, q+4 <= N, R[q:q+4] == R[pos:pos+4]   # conceptually
        qs = the 8 greatest such q (fewer if not available)
        for q in qs (descending, i.e. nearest first):
            L = largest L with 4 <= L <= min(65535, N-pos) and R[q+i] == R[pos+i] for all i < L
            # note: q+i may be >= pos; overlapping is allowed because R is fully known
            if L is greater than current best L: best = (q, L)
            # ties keep the earliest examined = greatest q = smallest offset
    if best exists:
        if pos > lit_start: emit token 0x00, varint(pos-lit_start), R[lit_start:pos]
        emit token 0x01, varint(pos-q), varint(L)
        pos = pos + L; lit_start = pos
    else:
        pos = pos + 1
if lit_start < N: emit token 0x00, varint(N-lit_start), R[lit_start:N]
```

`mode` selection: compute the canonical LZ token stream `T`; if `len(T) < N`, the block is stored with
`mode = 1`, `stored_len = len(T)` and `stored_payload = T`; otherwise `mode = 0`,
`stored_len = raw_len`, `stored_payload = R`. (Equal sizes → stored.)

### 4.5 Canonical block construction (`build`, `merge`, `recover` output)

Given the sorted, deduplicated records, blocks are formed as follows:

```
cur = []; cur_payload = b""; prev_key = b""
for record in sorted records:
    enc = encode_record(record, shared = (0 if cur is empty else min(255, common_prefix(prev_key, record.key_bytes))))
    if cur is not empty and len(cur_payload) + len(enc) > 8192:
        flush cur as a block
        cur = []; cur_payload = b""; prev_key = b""
        enc = encode_record(record, shared = 0)
    append record to cur; cur_payload += enc; prev_key = record.key_bytes
flush cur if non-empty
```

A single record whose encoding alone exceeds 8192 bytes forms a block by itself.
`build` of zero records produces a file with zero blocks.

---

## 5. Index (immediately after the last block, at `index_offset`)

`index_len` bytes: one entry per block, in block order, followed by a 4-byte CRC.

```
entry := varint(first_key_len)  first_key_bytes  u64(block_offset)
```

- `first_key` is the first record's key bytes of that block.
- `block_offset` is the absolute file offset of the block's first byte (`B`).
- Entries are in block order; `block_offset` values are strictly increasing; the first one is 32.
- `index_crc` (4 bytes at the end of the index) = `crc32c(the exact bytes of all entries)`.
- `index_len = (bytes of all entries) + 4`.

---

## 6. Footer (last 24 bytes of the file)

| offset | size | field          | value / meaning |
|-------:|-----:|----------------|-----------------|
| 0      | 8    | `index_offset` | `u64` |
| 8      | 4    | `index_len`    | `u32` |
| 12     | 4    | `footer_crc`   | `u32` = `crc32c(footer bytes[0:12])` |
| 16     | 8    | `footer_magic` | the 8 bytes `41 53 48 45 4E 44 30 31` (`"ASHEND01"`) |

The footer begins at `file_size - 24`.

---

## 7. Validity

A file is **valid** iff all of the following hold (this is precisely what `verify` checks, in the order of
§8):

1. Header checks: magic, version, flags, reserved, header CRC.
2. Footer present and its magic and CRC are correct; `index_offset >= 32`,
   `index_len >= 4`, `index_offset + index_len == file_size - 24`.
3. Blocks: starting at 32, zero or more blocks exactly fill `[32, index_offset)`; each block has valid
   framing, a valid CRC, a decodable payload, exactly `records` records, globally ascending keys, and
   respects all record limits.
4. `header.block_count` equals the number of blocks actually present in `[32, index_offset)`.
5. `header.record_count` equals the total number of records in those blocks.
6. Index: it has exactly `header.block_count` entries, each entry's `first_key` and `block_offset` agree
   with the corresponding block, the entries exactly fill `index_len - 4` bytes, and `index_crc` matches.

Validity deliberately does **not** require canonical form: a valid file may split records into blocks
differently from §4.5, may store a block uncompressed even when compression would shrink it, and may use
any LZ token stream that decodes correctly (not necessarily the one §4.4 would produce). `verify` accepts
any such file. Only the output of `build`, `merge` and `recover` must be canonical (byte-for-byte as §4.4
and §4.5 describe).

---

## 8. `verify`: error codes, offsets, precedence

`verify` checks in the following strict order and reports the **first** error found as
`ERR <CODE> <offset>` on stdout, exit code 1. A valid file reports `OK <record_count> <block_count>` on
stdout, exit code 0.

`offset` conventions:
- header field errors: the byte offset of that field in the file (see §3).
- footer errors: byte offset of the failing footer field (`file_size-24`, `file_size-16`,
  `file_size-12`, `file_size-8` as appropriate).
- block framing/CRC/payload/record errors: the byte offset of the block's first byte (`B`),
  except `BAD_BLOCK_CRC`, whose offset is the byte offset of the `block_crc` field
  (`B + 13 + stored_len`).
- index errors: the byte offset where the failing entry starts, or the documented CRC/len position.
- truncation errors: the current file size (for file-level truncation) or `B` (for block truncation).

Exact order of checks:

1. If `file_size < 32`: `TRUNCATED_HEADER  <file_size>`.
2. `BAD_MAGIC 0` / `BAD_VERSION 8` / `BAD_HEADER_FLAGS 10` / `BAD_RESERVED 12` / `BAD_HEADER_CRC 28`,
   in that order.
3. If `file_size < 56`: `TRUNCATED_FOOTER <file_size>`.
4. `BAD_FOOTER_MAGIC <file_size-8>`, then `BAD_FOOTER_CRC <file_size-12>`, then
   `BAD_INDEX_RANGE <file_size-24>` if `index_offset < 32`, or `index_len < 4`, or
   `index_offset + index_len != file_size - 24`.
5. Walk blocks from `cursor = 32` while `cursor < index_offset`:
   - `cursor + 13 > index_offset` → `BAD_BLOCK_TRUNCATED <cursor>`.
   - bytes are not `42 4C` → `BAD_BLOCK_MAGIC <cursor>`.
   - `mode > 1` → `BAD_BLOCK_MODE <cursor>`.
   - `records == 0` → `BAD_BLOCK_RECORDS <cursor>`.
   - `mode == 0 and stored_len != raw_len` → `BAD_BLOCK_SIZES <cursor>`.
   - `cursor + 17 + stored_len > index_offset` → `BAD_BLOCK_TRUNCATED <cursor>`.
   - block CRC mismatch → `BAD_BLOCK_CRC <cursor + 13 + stored_len>`.
   - `mode == 1`: decode LZ token stream (errors below; offset is `cursor`):
     `BAD_LZ_TOKEN`, `BAD_LZ_VARINT`, `BAD_LZ_LITERAL`, `BAD_LZ_MATCH`, `BAD_LZ_SIZE`,
     `BAD_LZ_TRUNCATED` (stored payload ran out before `raw_len`),
     `BAD_LZ_TRAILING` (stored payload bytes remain after `raw_len` output bytes).
     The decoded output length must equal `raw_len` (guaranteed by the above checks).
   - decode the record stream (errors below; offset is `cursor`):
     `RECORD_TRUNCATED` (a record needs bytes that are not there),
     `BAD_VARINT` (non-canonical or >u64 varint),
     `BAD_RECORD_FLAGS` (bits 1–7 set, or tombstone with `value_len != 0`),
     `BAD_SHARED` (`shared > len(previous key bytes)`; includes first record with `shared != 0`),
     `BAD_KEY_UTF8`, `BAD_KEY_NFC`, `BAD_LIMIT` (key > 4096 bytes),
     `BAD_T` (`t >= 2^53`),
     `BAD_LIMIT` (value > 1048576 bytes), `BAD_VALUE_UTF8`,
     `KEY_NOT_ASCENDING` (key ≤ previous record's key bytes, also across blocks).
     Check order within one record: exactly the order given in §4.2.
     Extra bytes after `records` records → `BAD_BLOCK_TAIL <cursor>`.
   - advance `cursor` by `17 + stored_len` and continue.
6. `block_count mismatch` → `BAD_BLOCK_COUNT 24`; then `record_count mismatch` → `BAD_RECORD_COUNT 16`
   (each compared against the count/sum discovered in step 5).
7. Parse the index using the actual block list: for each block index 0..`block_count-1`:
   entry truncated / key bytes or `u64` missing before `index_offset + index_len - 4` →
   `BAD_INDEX_TRUNCATED <entry_start>`; varint errors → `BAD_INDEX_TRUNCATED <entry_start>`;
   first_key or block_offset mismatch → `BAD_INDEX_ENTRY <entry_start>`.
   If the entries do not end exactly at `index_offset + index_len - 4` → `BAD_INDEX_LEN <pos>`.
8. `BAD_INDEX_CRC <index_offset + index_len - 4>` if the index CRC is wrong.

---

## 9. Commands, output formats, exit codes

`ledger.py <command> ...` — all messages below go to **stdout** (UTF-8); stderr is unspecified but
should stay empty. Exit codes: 0 success; 1 verify failure; 2 ledger-file format error; 3 usage error;
4 input-data error; 5 I/O error.

**I/O errors:** if a command cannot read or write a required file (missing file, permission error, etc.) it
prints `ERR IO` and exits 5. This applies to every command.

### 9.1 `build <input.ndjson> <output.algr>`
Reads the NDJSON file (§10), deduplicates, sorts, and writes the canonical ledger to `output`.
On success: no stdout, exit 0; the output file is created/overwritten.
On input-data error: `ERR INPUT <lineno> <CODE>`, exit 4, and the output file must **not** be created
(if it already existed, it must be left unchanged — write atomically).
On file I/O failure: `ERR IO`, exit 5.

### 9.2 `get <file.algr> <key> [<key> ...]`
The ledger must be valid; otherwise `ERR <CODE> <offset>`, exit 2.
For each key argument, in argument order: normalize to NFC, look it up. If the key is present and alive,
print `json.dumps(value, ensure_ascii=False)` on one line. If the key is a tombstone or absent, print
`null`. Exit 0. (No extra spaces; Python's `json.dumps` default separators for a string are irrelevant.
`ensure_ascii=False`, and the line ends with exactly one `\n`.)

### 9.3 `scan <file.algr> [--from <key>] [--limit <n>]`
The ledger must be valid; otherwise `ERR <CODE> <offset>`, exit 2.
Print one line per selected record, in ledger order (ascending key bytes):

```
json.dumps({"k": <key str>, "v": <value str or None>, "t": <t int>}, ensure_ascii=False)
```

i.e. a JSON object with exactly the members `k`, `v`, `t` in that order, then `\n`. Tombstones print
`"v": null`. `--from` (optional): only records whose key bytes are ≥ the NFC-normalized `--from` key's
UTF-8 bytes. `--limit` (optional, non-negative decimal integer): print at most that many records.
The flags may appear in either order after the file. Exit 0.

### 9.4 `verify <file.algr>`
As specified in §8. Valid: `OK <record_count> <block_count>`, exit 0.
Invalid: `ERR <CODE> <offset>`, exit 1.

### 9.5 `recover <input.algr> <output.algr>`
Crash recovery. Read the whole input. If `file_size < 32` → `ERR TRUNCATED_HEADER <file_size>`, exit 2.
If the magic or version is wrong → `ERR BAD_MAGIC 0` / `ERR BAD_VERSION 8`, exit 2.
The header CRC, flags, reserved field and both counts are **ignored** by `recover`.
Starting at offset 32, repeatedly attempt to decode a block exactly as a valid block (§4.1–4.2): framing,
CRC, payload, records, and the records must continue the ascending key order after the previously
recovered records. Stop at the first byte offset where the block cannot be decoded for any reason
(including reaching the end of the file, or the two bytes not being `"BL"`). All records from the fully
decoded prefix blocks are recovered.
Write a **canonical** ledger (as if built from the recovered records, §4.5) to `output`, print
`RECOVERED <n>` (`n` = number of recovered records), exit 0. `recover` always succeeds for well-formed
header magic/version, even if zero records are recovered.

### 9.6 `merge <output.algr> <input1.algr> [<input2.algr> ...]`
All inputs must be valid; if an input is invalid, report its error as `ERR <CODE> <offset>` (first invalid
input in argument order), exit 2, and do not create/modify `output`. Combine all records: for equal keys
(normalized), the record with the **greater `t`** wins; if `t` is equal, the record from the **later**
input file wins; ties within one file are impossible for a valid input. Write the canonical merged ledger;
no stdout; exit 0.

### 9.7 `info <file.algr>`
The ledger must be valid; otherwise `ERR <CODE> <offset>`, exit 2.
Print `json.dumps({"records": <record_count>, "blocks": <block_count>, "bytes": <file_size>})` then `\n`.
(Field order as written; Python default separators.)

### 9.8 Usage errors
Bad command, missing/extra arguments, malformed `--limit`, unknown flags → `ERR USAGE`, exit 3.

---

## 10. Input NDJSON (`build`)

The input file is decoded as UTF-8. It is split on `0x0A`; an optional single `0x0D` immediately before
each `0x0A` is removed; a final line without a trailing newline is still a line; a trailing newline at
end of file does **not** create an extra empty line. **Every** line must be a JSON object with exactly
three members: `k` (string), `v` (string or null), `t` (integer).

Validation per line (1-based `lineno`); first failure aborts with `ERR INPUT <lineno> <CODE>`, exit 4:

- `INPUT_JSON`: line is not valid JSON or is not an object. JSON is strict (RFC 8259): the non-standard
  constants `NaN`, `Infinity` and `-Infinity` are **not** valid JSON and produce `INPUT_JSON`. Bytes that
  are not valid UTF-8 produce `INPUT_JSON` for the first affected line.
- `INPUT_SCHEMA`: member set is not exactly `{"k","v","t"}` or a member has the wrong JSON type
  (`k` must be string; `v` must be string or null; `t` must be a JSON integer — a number written with a
  fraction or exponent such as `1.0` or `1e3` is not a JSON integer and produces `INPUT_SCHEMA`, as does a
  boolean).
- `INPUT_KEY`: key is a string but its NFC form is longer than 4096 UTF-8 bytes, or the key contains an
  unpaired UTF-16 surrogate (e.g. from a `\ud800` escape) and therefore cannot be encoded as UTF-8.
- `INPUT_VALUE`: value is a string longer than 1048576 UTF-8 bytes, or contains an unpaired surrogate.
- `INPUT_T`: `t` is an integer but `t < 0` or `t >= 2^53`.

Duplicate member names inside one JSON object are not permitted; behaviour for such lines is unspecified
and they are never tested.

Deduplication (build): process lines in order; for a repeated normalized key, the record with the greater
`t` replaces the previous one; if `t` is equal, the later line replaces the previous one.
(Consequence: the earlier line wins whenever its `t` is strictly greater.)
Output records are sorted by key UTF-8 bytes ascending.

---

## 11. Limits summary

| item | limit |
|------|-------|
| key bytes (after NFC) | ≤ 4096 |
| value bytes | ≤ 1048576 |
| `t` | 0 ≤ t < 2^53 |
| `records` per block | 1 … 65535 |
| `raw_len`, `stored_len` | u32 |
| block raw payload (canonical) | ≤ 8192 unless a single record is larger |

---

## 12. Examples

Canonical byte-for-byte examples for a few inputs are in `samples/` (`input.ndjson` + `expected.algr`):
an empty ledger, a small Unicode ledger (plus the exact bytes its `scan` prints), and a torn-file example
with its expected recovery result. These are illustrative only — they do **not** cover the whole format;
every other byte must be derived from the rules above.

Determinism requirement: two runs of `build` on the same input must produce identical files; `merge` of the
same inputs must equal a canonical `build` of the combined records under the rules of §9.6.

---

## 13. Normative clarifications (v1.2)

These clarifications are part of the specification; they remove possible second readings. They do not
change any behaviour described above.

1. **Varint canonicality** is as in §1.2: a multi-byte encoding ending in `0x00` is non-canonical. An
   encoding of 10 bytes with a continuation bit on the 10th byte, or any encoding decoding above
   2^64−1, is invalid.
2. **Record varint truncation vs malformed varint (§4.2 step 2).** If the payload ends while a varint is
   incomplete → `RECORD_TRUNCATED`. If the varint is already malformed at the point where it can be
   decided (an 11th byte is required, or the 10-byte value exceeds `u64`) → `BAD_VARINT`, even if the
   payload also ends nearby.
3. **§4.2 step 3 uses flags bit 0 only.** Bits 1–7 being set does not change how many bytes the
   truncation test in step 3 requires.
4. **Missing value bytes are always `RECORD_TRUNCATED` (step 3)**, never `BAD_LIMIT`/`BAD_VALUE_UTF8`,
   even when `value_len` also exceeds 1 048 576.
5. **§4.4 candidate index covers every position.** Before searching at position `pos`, the candidate
   lists contain every position `q < pos` with `q+4 <= N` — including positions inside regions that were
   already emitted as back-references or literals. The index is filled for every position, not only for
   the positions visited by the scan loop.
6. **`BAD_INDEX_LEN <pos>`**: `pos` is the offset immediately after the last parsed index entry, i.e. the
   first unconsumed index byte.
7. **Index varint errors:** in the index, every varint failure (truncated, non-canonical, or >`u64`) is
   reported as `BAD_INDEX_TRUNCATED` at the entry start, never `BAD_VARINT`.
8. **`--limit` grammar (§9.3/§9.8):** exactly one ASCII-digit string `[0-9]+` (leading zeros allowed;
   `007` means 7). `+3`, ` 3`, `3 `, `3_0`, `0x10` are `ERR USAGE`. Each flag may appear at most once.
   Attached forms such as `--from=...` and `--limit=...`, and `--`, are `ERR USAGE`. Flags must follow
   the file argument; a flag in the command position after `scan` is `ERR USAGE`.
9. **Literal arguments:** key arguments, `--from` values and `--limit` values are taken literally from
   argv and are never interpreted as flags. `get f --help` looks up the key `--help`; `scan f --from -x`
   filters from the key `-x`; an empty-string argument is an empty key; `--` has no special meaning.
10. **Leading UTF-8 BOM (§10):** a BOM is not stripped; it makes line 1 invalid JSON → `INPUT_JSON 1`.
11. **CR handling (§10):** a CR is removed only when immediately followed by `0x0A` as the line
    terminator. A CR at the end of a final line without a newline remains part of the line (JSON accepts
    it as trailing whitespace). An empty CRLF line (e.g. `...\r\n\r\n`) is an empty line → `INPUT_JSON`
    for that line number.
12. **Per-line build error precedence (§10):** within one line, report the first of
    `INPUT_JSON` → `INPUT_SCHEMA` → `INPUT_KEY` → `INPUT_VALUE` → `INPUT_T`; the first failing line
    aborts the build. A line with both an over-long key and an out-of-range `t` is `INPUT_KEY`.
13. **`ERR IO` scope:** includes paths that exist but are directories or cannot be opened in the
    required mode. For `build`, a write failure reports `ERR IO`, exit 5, and leaves any pre-existing
    output file untouched.
