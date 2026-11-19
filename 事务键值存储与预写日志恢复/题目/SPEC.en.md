# 事务键值存储与预写日志恢复 / Transactional Key-Value Storage and Write-Ahead Log Recovery

Fix a single-process key-value database whose transactions can interleave. Correct snapshot visibility, commit conflict detection, and recovery after interrupted writes. A replacement implementation is allowed. Retain the entry point `chronicle.py`.

## Running and testing

```text
python -B chronicle.py --db data
python -B -m pytest public_tests -q -p no:cacheprovider
```

The second command runs the public tests and requires pytest.

The test environment is Windows with CPython 3.14.2. Use only the Python standard library. The program may not use an external database, spawn other processes, or access the network. The only persistent database state is `journal.wal` in the `--db` directory. In-memory indexing is allowed.

Use UTF-8 NDJSON with one object per line. Output and flush one response immediately after processing each input. Standard output contains only responses. At EOF, discard uncommitted transactions and exit normally. Diagnostics may go to stderr.

Multiple Python files are allowed. The program cannot depend on any other resource file. Inputs conform to the protocol and transaction lifecycle. Handling malformed JSON, invalid transaction IDs or savepoints, concurrent database processes, and disk I/O failures is outside the input contract.

## Data and versions

Keys and values are strings of Unicode scalar values. Empty strings, NUL, newlines, and non-ASCII characters are allowed. Do not apply Unicode normalization. Order keys lexicographically by unsigned UTF-8 bytes. An absent key yields JSON `null`. The empty value `""` is present.

The global commit version starts at 0. `begin` fixes the transaction snapshot. Later reads use the committed state at that version overlaid by pending writes in the same transaction. Other commits do not alter the snapshot. Do not copy the whole database at `begin`. Many long transactions may overlap with many short ones.

Each transaction has a write overlay containing its last `put` or `delete` for each touched key. Deleting an absent key still records a write. A successful commit with a nonempty overlay increments the version even if the visible value is unchanged. A commit with an empty overlay returns the current global version without incrementing it.

## Commands

The right column specifies each complete response. `tx` and `name` are nonempty strings.

| Input | Response |
| --- | --- |
| `{"op":"begin","tx":"a"}` | `{"ok":true,"version":V}`, where V is the current global version |
| `{"op":"get","tx":"a","key":"k"}` | `{"value":S}` with a string or null |
| `{"op":"scan","tx":"a","start":"a","end":"z"}` | `{"items":[["key","value"],...]}` |
| `{"op":"put","tx":"a","key":"k","value":"v"}` | `{"ok":true}` |
| `{"op":"delete","tx":"a","key":"k"}` | `{"ok":true}` |
| `{"op":"savepoint","tx":"a","name":"s"}` | `{"ok":true}` |
| `{"op":"rollback","tx":"a","name":"s"}` | `{"ok":true}` |
| `{"op":"abort","tx":"a"}` | `{"ok":true}` |
| `{"op":"commit","tx":"a"}` | `{"ok":true,"version":V}` on success or `{"ok":false,"error":"conflict"}` on conflict |

`scan` returns all visible key-value pairs in the half-open interval `[start,end)` in ascending order, excluding deleted keys. A null start or end represents negative or positive infinity, respectively. Equal endpoints return an empty result, but still register the empty interval. Non-null endpoints satisfy `start <= end`. Do not use string sentinels for infinities.

`savepoint` pushes the current write overlay. Active savepoint names are distinct. `rollback` restores the named overlay, discards newer savepoints, and retains the named savepoint for reuse. Neither operation changes the snapshot version.

Read dependencies survive rollback. Record every `get`, including reads of absent keys or of the transaction's own writes. Record the whole range of every `scan`, even with no results or only self-written results.

A commit ends the transaction whether it succeeds or conflicts. An abort ends it as well. An ended transaction ID may be reused.

## Conflict checks at commit

Let S be the version at transaction start. Reject the whole transaction if a key was touched by a successful write transaction after S and that key satisfies at least one condition:

1. It is in the committing transaction's write overlay.
2. It was the subject of any `get` in that transaction.
3. It lies within any interval registered by that transaction's `scan`.

Touched keys include deletions of absent keys, writes of identical values, deletions followed by recreation, and changes later reversed. Comparing only the current and snapshot values is insufficient. Check already committed transactions only. A conflict applies atomically, with no partial writes. Read-only transactions use the same read dependency checks. A key outside the dependencies does not conflict. The upper endpoint of a scan is excluded.

## Write-ahead log binary format

`journal.wal` is the only persisted state and must remain compatible with existing files. Initialize a missing or zero-length log with this 8-byte header:

```text
43 48 52 4f 4e 31 0d 0a    # b"CHRON1\r\n"
```

A nonempty file has a valid header. It is followed by zero or more frames. Integer fields are unsigned, fixed-width, and little-endian.

```text
frame := payload_length:u32 | payload:bytes | crc32:u32
crc32 := zlib.crc32(payload) & 0xffffffff

payload := commit_version:u64 | operation_count:u32 | operation*
put     := tag:u8=1 | key_length:u32 | key:utf8 | value_length:u32 | value:utf8
delete  := tag:u8=2 | key_length:u32 | key:utf8
```

A valid payload is 12 through 8,388,608 bytes, with at least one operation. Within a frame, encoded keys are strictly increasing, so duplicates are invalid. UTF-8 must be valid and decoding must consume the whole payload. Commit versions start at 1 and increase by 1 per frame. A successful nonempty write commits exactly one frame containing the final overlay. Conflicts, aborts, and read-only commits append no frame.

At startup, replay the longest contiguous valid frame prefix following the header. Stop at the first truncation, invalid length or CRC, malformed operation or UTF-8, duplicate or out-of-order key, zero operation count, incorrect version, or trailing payload bytes. Do not scan for frames beyond that point. Truncate to the end of the valid prefix, flush, and call `os.fsync` before accepting commands. Preserve the existing bytes in the valid prefix.

At commit, check conflicts, encode and append the frame, flush, call `os.fsync`, publish the in-memory state, and return success, in that order. An acknowledged commit must be visible after an immediate forced exit and restart. Disk I/O failure handling and physical power-loss simulation are outside the requirements. Do not rewrite, compress, or reorder existing valid frames.

## Scale and resource limits

Each valid frame is at most 8 MiB. The WAL is at most 64 MiB. There are at most 30,000 distinct keys, 100,000 committed versions, and 2,000 concurrent active transactions. Inputs may contain long Unicode strings. Total input is bounded, and collecting all unreachable version history is optional.

The stress scenario includes approximately 25,000 preloaded keys, 1,500 long-running snapshots, and interleaved commits. It has a 25-second limit. Other scenarios have a 15-second limit. The database subprocess has a 320 MiB peak working-set limit. Snapshots may share version histories.

## Two interleavings

1. A scans `["m","n")` and sees no records. B writes `"moon"` and commits. A's next scan still sees no records, but committing A conflicts.
2. A creates a savepoint, reads absent key `"ghost"`, and rolls back. B deletes `"ghost"` and commits. A still conflicts. An empty interval such as `["x","x")` cannot conflict on a range dependency.
