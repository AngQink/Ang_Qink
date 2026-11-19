import json
import random
import sys
from pathlib import Path

from support import HEADER, Model, Session, c, pack_frame, wrap_payload

CASES = []


def case(group, name):
    def register(fn):
        CASES.append((group, name, fn))
        return fn
    return register


@case("semantics", "unicode_empty_values_and_restart")
def unicode_values(r):
    pairs = {"": "", "\0": "nul\0line\n", "药": "学😀", "e\u0301": "decomposed",
             "é": "composed", "\U0010ffff": "last", "\uffff": "bmp", "😀": "astral"}
    commands = [c("begin")] + [c("put", key=k, value=v) for k, v in pairs.items()]
    commands += [c("scan", start=None, end=None), c("commit")]
    model, db = r.check(commands)
    r.check([c("begin"), c("scan", start=None, end=None), c("get", key="absent"), c("commit")], model, db)


@case("semantics", "stable_snapshot_overlay_and_sorted_scan")
def stable_overlay(r):
    r.check([c("begin", "seed"), c("put", "seed", key="b", value="old"), c("commit", "seed"),
             c("begin"), c("begin", "b"), c("put", "b", key="b", value="new"),
             c("put", "b", key="c", value="new"), c("commit", "b"), c("get", key="b"),
             c("put", key="a", value="own"), c("delete", key="b"),
             c("scan", start=None, end=None), c("abort")])


@case("semantics", "readonly_version_and_transaction_id_reuse")
def readonly_and_reuse(r):
    r.check([c("begin"), c("begin", "b"), c("put", "b", key="k", value="v"),
             c("commit", "b"), c("commit"), c("begin"), c("abort"), c("begin"), c("commit"),
             c("begin"), c("delete", key="missing"), c("commit"), c("begin"), c("commit")])


@case("semantics", "eof_aborts_uncommitted_data")
def eof_aborts(r):
    model, db = r.check([c("begin", "seed"), c("put", "seed", key="k", value="saved"),
                         c("commit", "seed"), c("begin"), c("put", key="k", value="uncommitted")])
    model.tx.clear()
    r.check([c("begin"), c("get", key="k"), c("commit")], model, db)


@case("occ", "write_write_same_value_and_atomic_rejection")
def write_conflict(r):
    r.check([c("begin"), c("put", key="k", value="same"), c("put", key="other", value="must-not-leak"),
             c("begin", "b"), c("put", "b", key="k", value="same"), c("commit", "b"),
             c("commit"), c("begin", "read"), c("get", "read", key="other"), c("commit", "read")])


@case("occ", "write_skew_is_rejected")
def write_skew(r):
    r.check([c("begin", "seed"), c("put", "seed", key="x", value="1"),
             c("put", "seed", key="y", value="1"), c("commit", "seed"),
             c("begin"), c("begin", "b"), c("get", key="y"), c("get", "b", key="x"),
             c("put", key="x", value="0"), c("put", "b", key="y", value="0"),
             c("commit"), c("commit", "b")])


@case("occ", "aba_value_restored_still_conflicts")
def aba(r):
    r.check([c("begin", "seed"), c("put", "seed", key="k", value="same"), c("commit", "seed"),
             c("begin"), c("get", key="k"), c("begin", "b"), c("delete", "b", key="k"),
             c("commit", "b"), c("begin", "b"), c("put", "b", key="k", value="same"),
             c("commit", "b"), c("get", key="k"), c("commit")])


@case("occ", "absent_tombstone_conflicts_with_absent_read")
def absent_tombstone(r):
    r.check([c("begin"), c("get", key="missing"), c("begin", "b"),
             c("delete", "b", key="missing"), c("commit", "b"), c("commit")])


@case("occ", "empty_scan_phantom_then_delete")
def phantom_then_delete(r):
    r.check([c("begin"), c("scan", start="m", end="n"), c("begin", "b"),
             c("put", "b", key="moon", value="v"), c("commit", "b"), c("begin", "b"),
             c("delete", "b", key="moon"), c("commit", "b"), c("scan", start="m", end="n"), c("commit")])


@case("occ", "scan_conflicts_on_deleted_preexisting_key")
def range_delete(r):
    r.check([c("begin", "seed"), c("put", "seed", key="m", value="v"), c("commit", "seed"),
             c("begin"), c("scan", start="m", end="n"), c("begin", "b"),
             c("delete", "b", key="m"), c("commit", "b"), c("scan", start="m", end="n"), c("commit")])


@case("occ", "bounds_are_half_open_and_empty_intervals_are_empty")
def precise_bounds(r):
    r.check([c("begin"), c("scan", start="m", end="n"), c("scan", start="x", end="x"),
             c("begin", "b"), c("put", "b", key="n", value="upper-bound"),
             c("put", "b", key="x", value="empty-interval"), c("put", "b", key="a", value="outside"),
             c("commit", "b"), c("commit"), c("begin"), c("scan", start=None, end=""),
             c("begin", "b"), c("delete", "b", key=""), c("commit", "b"), c("commit")])


@case("occ", "unbounded_scan_includes_maximum_unicode_key")
def unbounded_unicode(r):
    r.check([c("begin"), c("scan", start="\uffff", end=None), c("begin", "b"),
             c("put", "b", key="\U0010ffffmore", value="far"), c("commit", "b"), c("commit")])


@case("occ", "reads_of_own_writes_still_register_dependencies")
def own_write_read(r):
    r.check([c("begin"), c("savepoint", name="before"), c("put", key="k", value="own"),
             c("get", key="k"), c("rollback", name="before"), c("begin", "b"),
             c("put", "b", key="k", value="other"), c("commit", "b"), c("commit")])


@case("savepoints", "nested_rollback_retains_target_and_can_repeat")
def nested_savepoint(r):
    r.check([c("begin"), c("put", key="k", value="first"), c("savepoint", name="outer"),
             c("put", key="k", value="second"), c("savepoint", name="inner"),
             c("delete", key="k"), c("rollback", name="inner"), c("get", key="k"),
             c("rollback", name="outer"), c("get", key="k"), c("put", key="extra", value="x"),
             c("rollback", name="outer"), c("savepoint", name="inner"), c("scan", start=None, end=None),
             c("commit")])


@case("savepoints", "rollback_preserves_point_reads")
def rollback_reads(r):
    r.check([c("begin"), c("savepoint", name="s"), c("get", key="ghost"), c("rollback", name="s"),
             c("begin", "b"), c("delete", "b", key="ghost"), c("commit", "b"), c("commit")])


@case("savepoints", "rollback_preserves_entire_scan_not_only_returned_keys")
def rollback_ranges(r):
    r.check([c("begin"), c("savepoint", name="s"), c("put", key="ma", value="own"),
             c("scan", start="m", end="n"), c("rollback", name="s"), c("begin", "b"),
             c("delete", "b", key="mz"), c("commit", "b"), c("commit")])


@case("savepoints", "rolled_back_blind_writes_create_no_dependencies")
def rollback_blind(r):
    r.check([c("begin"), c("savepoint", name="s"), c("put", key="k", value="gone"),
             c("rollback", name="s"), c("begin", "b"), c("put", "b", key="k", value="other"),
             c("commit", "b"), c("commit")])


@case("wal", "valid_external_frames_and_exact_prefix_preservation")
def external_frames(r):
    model = Model()
    model.seed({"z": "old", "药": "药\0\n😀", "": "empty-key", "absent": None})
    model.seed({"z": None, "a": "new", "药": ""})
    db = r.new_db(model.expected_wal)
    r.check([c("begin"), c("scan", start=None, end=None), c("put", key="later", value="third"), c("commit")], model, db)


def bad_frame_case(name, bad):
    @case("wal", "reject_" + name)
    def check(r):
        model = Model()
        model.seed({"a": "valid-prefix", "tombstone": None})
        suffix = bad() if callable(bad) else bad
        # Valid-looking frames after corruption must never be discovered by resync.
        suffix += pack_frame(2, [("smuggled", "forbidden")]) + pack_frame(3, [("tail", "forbidden")])
        db = r.new_db(model.expected_wal + suffix)
        r.check([c("begin"), c("get", key="smuggled"), c("get", key="a"),
                 c("put", key="repaired", value="yes"), c("commit")], model, db)


def payload(version=2, count=1):
    return version.to_bytes(8, "little") + count.to_bytes(4, "little")


valid_second = pack_frame(2, [("k", "value")])
for n in [1, 2, 3, 4, 7, 12, len(valid_second) - 5, len(valid_second) - 1]:
    bad_frame_case(f"torn_frame_at_{n}", valid_second[:n])
for n in [0, 11, 8_388_609, 0xffffffff]:
    bad_frame_case(f"payload_length_{n}", n.to_bytes(4, "little"))
bad_frame_case("crc_mismatch", valid_second[:-1] + bytes([valid_second[-1] ^ 0x80]))
for tag in [0, 3, 255]:
    bad_frame_case(f"tag_{tag}", wrap_payload(payload() + bytes([tag]) + b"\0\0\0\0"))
bad_frame_case("zero_operations", wrap_payload(payload(count=0)))
bad_frame_case("trailing_payload_bytes", wrap_payload(valid_second[4:-4] + b"extra"))
bad_frame_case("duplicate_keys", pack_frame(2, [("x", "one"), ("x", "two")]))
bad_frame_case("unsorted_keys", pack_frame(2, [("z", "one"), ("a", "two")]))
for version in [0, 1, 3, 2**64 - 1]:
    bad_frame_case(f"version_{version}", pack_frame(version, [("k", "v")]))
bad_frame_case("overlong_utf8_key", wrap_payload(payload() + b"\x02\x02\0\0\0\xc0\xaf"))
bad_frame_case("surrogate_utf8_key", wrap_payload(payload() + b"\x02\x03\0\0\0\xed\xa0\x80"))
bad_frame_case("invalid_utf8_value", wrap_payload(payload() + b"\x01\x01\0\0\0k\x01\0\0\0\xff"))
bad_frame_case("short_key", wrap_payload(payload() + b"\x02\x09\0\0\0k"))
bad_frame_case("short_value", wrap_payload(payload() + b"\x01\x01\0\0\0k\x09\0\0\0v"))
bad_frame_case("too_few_operations", wrap_payload(payload(count=2) + b"\x02\x01\0\0\0k"))
bad_frame_case("huge_operation_count", wrap_payload(payload(count=0xffffffff)))
bad_frame_case("unconsumed_operation", wrap_payload(payload(count=1) + b"\x02\x01\0\0\0a\x02\x01\0\0\0b"))


@case("wal", "empty_file_and_header_only_startup")
def empty_files(r):
    for raw in [b"", HEADER]:
        model = Model()
        db = r.new_db(raw)
        r.check([c("begin"), c("get", key="k"), c("commit")], model, db)


@case("wal", "maximum_legal_payload_length")
def max_payload(r):
    value = "x" * (8_388_608 - 22)
    frame = pack_frame(1, [("k", value)])
    assert len(frame) == 8_388_608 + 8
    db = r.new_db(HEADER + frame)
    actual, _ = r.run([c("begin"), c("get", key="k"), c("commit")], db)
    assert actual == [{"ok": True, "version": 1}, {"value": value}, {"ok": True, "version": 1}]
    assert (db / "journal.wal").read_bytes() == HEADER + frame


@case("wal", "large_unicode_fields_use_byte_lengths")
def large_unicode(r):
    model, db = r.check([c("begin"), c("put", key="药" * 25000, value="😀\0\n" * 50000), c("commit")])
    r.check([c("begin"), c("get", key="药" * 25000), c("commit")], model, db)


@case("wal", "fifty_thousand_external_versions_recover_in_order")
def many_versions(r):
    frames = [pack_frame(i, [("hot", None if i % 3 == 0 else str(i))]) for i in range(1, 50001)]
    prefix = HEADER + b"".join(frames)
    db = r.new_db(prefix)
    result, _ = r.run([c("begin"), c("get", key="hot"), c("put", key="other", value="new"), c("commit")], db)
    assert result == [{"ok": True, "version": 50000}, {"value": "50000"}, {"ok": True}, {"ok": True, "version": 50001}]
    assert (db / "journal.wal").read_bytes() == prefix + pack_frame(50001, [("other", "new")])


def random_case(seed):
    @case("randomized", f"interleaved_model_seed_{seed}")
    def check(r):
        rng = random.Random(seed)
        model = Model()
        db = r.new_db()
        keys = ["", "a", "ab", "b", "ghost", "m", "moon", "n", "z", "\0", "é", "e\u0301", "药", "😀", "\U0010ffff"]
        labels = 0
        for phase in range(3):
            commands, expected = [], []
            for _ in range(450):
                if not model.tx or (len(model.tx) < 10 and rng.random() < 0.2):
                    name = next(f"t{i}" for i in range(11) if f"t{i}" not in model.tx)
                    command = c("begin", name)
                else:
                    name = rng.choice(sorted(model.tx))
                    t = model.tx[name]
                    choice = rng.randrange(100)
                    if choice < 21:
                        command = c("put", name, key=rng.choice(keys), value=rng.choice(["", "v", "药\0\n😀", str(rng.randrange(10))]))
                    elif choice < 34:
                        command = c("delete", name, key=rng.choice(keys))
                    elif choice < 51:
                        command = c("get", name, key=rng.choice(keys))
                    elif choice < 68:
                        lo, hi = sorted(rng.choices(keys, k=2), key=lambda s: s.encode("utf-8"))
                        command = c("scan", name, start=None if rng.random() < .2 else lo,
                                    end=None if rng.random() < .2 else hi)
                    elif choice < 78:
                        labels += 1
                        command = c("savepoint", name, name=f"s{labels}")
                    elif choice < 86 and t["save"]:
                        command = c("rollback", name, name=rng.choice(t["save"])[0])
                    elif choice < 96:
                        command = c("commit", name)
                    else:
                        command = c("abort", name)
                commands.append(command)
                expected.append(model.execute(command))
            actual, _ = r.run(commands, db)
            for index, (want, got) in enumerate(zip(expected, actual)):
                assert got == want, f"seed={seed} phase={phase} command={index} {commands[index]!r}: {want!r} != {got!r}"
            assert (db / "journal.wal").read_bytes() == model.expected_wal, "random schedule WAL mismatch"
            model.tx.clear()
            # Crashed uncommitted tail between sessions, never a legal frame.
            if phase < 2:
                with (db / "journal.wal").open("ab") as stream:
                    stream.write(b"\xff\xff\xff\xff" + rng.randbytes(17))
        r.check([c("begin"), c("scan", start=None, end=None), c("commit")], model, db)


for seed in [17, 1017, 2026, 271828, 314159, 65537, 900001, 123456789]:
    random_case(seed)


@case("durability", "reply_is_immediate_and_acknowledged_commit_survives_kill")
def kill_after_ack(r):
    db = r.new_db()
    session = Session(r.candidate, db)
    try:
        assert session.ask(c("begin")) == {"ok": True, "version": 0}
        assert session.ask(c("put", key="k", value="committed😀")) == {"ok": True}
        assert session.ask(c("commit")) == {"ok": True, "version": 1}
        assert session.ask(c("begin")) == {"ok": True, "version": 1}
        assert session.ask(c("put", key="k", value="uncommitted")) == {"ok": True}
    finally:
        session.kill()
    model = Model()
    model.seed({"k": "committed😀"})
    r.check([c("begin"), c("get", key="k"), c("commit")], model, db)


@case("durability", "actual_wal_fsync_precedes_commit_ack_and_recovery_input")
def audit_fsync(r):
    model = Model()
    model.seed({"a": "prefix"})
    prefix = model.expected_wal
    db = r.new_db(prefix + b"\x40\x00")
    trace = r.workspace / "fsync-events.jsonl"
    driver = Path(__file__).with_name("audit_driver.py")
    commands = [c("begin"), c("put", key="b", value="saved"), c("commit")]
    expected = [model.execute(cmd) for cmd in commands]
    actual, _ = r.run(commands, db, launch=[sys.executable, str(driver), str(trace)])
    assert actual == expected
    events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    first_output = next(i for i, e in enumerate(events) if "output" in e)
    assert {"sync": len(prefix)} in events[:first_output], "tail repair was not fsynced before first reply"
    commit_output = next(i for i, e in enumerate(events) if e.get("output") == {"ok": True, "version": 2})
    assert {"sync": len(model.expected_wal)} in events[:commit_output], "WAL fsync did not precede commit ack"
    assert (db / "journal.wal").read_bytes() == model.expected_wal


@case("resources", "25000_keys_1500_snapshots_and_interleaved_commits")
def many_snapshots(r):
    initial = {f"k{i:05d}": "x" * 120 + str(i) for i in range(25000)}
    prefix = HEADER + pack_frame(1, list(initial.items()))
    db = r.new_db(prefix)
    commands, expected = [], []
    at_begin = []
    version, value = 1, initial["k00000"]

    def add(command, response):
        commands.append(command)
        expected.append(response)

    for i in range(1500):
        tx = f"long-{i}"
        add(c("begin", tx), {"ok": True, "version": version})
        at_begin.append(value)
        add(c("begin", "writer"), {"ok": True, "version": version})
        value = f"version-{i}"
        add(c("put", "writer", key="k00000", value=value), {"ok": True})
        version += 1
        add(c("commit", "writer"), {"ok": True, "version": version})
        add(c("get", tx, key="k00000"), {"value": at_begin[-1]})
    for i, old in enumerate(at_begin):
        add(c("get", f"long-{i}", key="k00000"), {"value": old})
        add(c("abort", f"long-{i}"), {"ok": True})
    actual, _ = r.run(commands, db, timeout=25)
    assert actual == expected, "long snapshot values or versions are incorrect"
    tail = b"".join(pack_frame(i + 2, [("k00000", f"version-{i}")]) for i in range(1500))
    assert (db / "journal.wal").read_bytes() == prefix + tail
