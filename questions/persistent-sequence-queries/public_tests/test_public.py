import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
P, B = 1000000007, 911382323


def stats(values):
    n = len(values)
    return dict(n=n, sum=sum(values) % P, square=sum(x*x for x in values) % P,
                moment=sum(i*x for i, x in enumerate(values)) % P,
                forward=sum(x*pow(B, i, P) for i, x in enumerate(values)) % P,
                backward=sum(x*pow(B, n-1-i, P) for i, x in enumerate(values)) % P)


def run(commands):
    data = ''.join(json.dumps(c)+'\n' for c in commands).encode()
    result = subprocess.run([sys.executable, str(ROOT/'loom.py')], input=data,
                            capture_output=True, timeout=8, cwd=ROOT)
    if result.returncode or result.stderr:
        raise AssertionError((result.returncode, result.stderr.decode('utf-8', errors='replace')))
    assert b'\r' not in result.stdout
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(replies) == len(commands)
    return replies


class PublicTests(unittest.TestCase):
    def test_sample(self):
        commands = [json.loads(x) for x in (ROOT/'samples/demo.ndjson').read_text(encoding='utf-8').splitlines()]
        expected = [json.loads(x) for x in (ROOT/'samples/demo.expected.ndjson').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(run(commands), expected)

    def test_local_coordinates_reverse_and_snapshot(self):
        actual = run([dict(op='new', values=[2, 5, 7]),
                      dict(op='edit', v=1, l=1, r=3, a=2, b=3, c=4),
                      dict(op='reverse', v=2, l=0, r=3),
                      dict(op='query', v=1, l=0, r=3),
                      dict(op='query', v=2, l=1, r=3),
                      dict(op='query', v=3, l=0, r=3)])
        self.assertEqual(actual[-3:], [stats([2, 5, 7]), stats([13, 21]), stats([21, 13, 2])])

    def test_overlapping_self_splice(self):
        actual = run([dict(op='new', values=[1, 2, 3, 4]),
                      dict(op='splice', v=1, l=1, r=3, src=1, sl=0, sr=3),
                      dict(op='query', v=2, l=0, r=5), dict(op='query', v=1, l=0, r=4)])
        self.assertEqual(actual[-2:], [stats([1, 1, 2, 3, 4]), stats([1, 2, 3, 4])])

    def test_aliases_survive_edits_and_drop(self):
        actual = run([dict(op='new', values=[1, 2, 3]), dict(op='concat', left=1, right=1),
                      dict(op='edit', v=2, l=1, r=5, a=0, b=8, c=3), dict(op='drop', v=1),
                      dict(op='query', v=2, l=0, r=6), dict(op='query', v=3, l=0, r=6)])
        self.assertEqual(actual[-2:], [stats([1, 2, 3, 1, 2, 3]), stats([1, 8, 11, 14, 17, 3])])

    def test_huge_repeat_and_rank_ramp(self):
        n = 2**55
        last = (1+2*(n-1)) % P
        actual = run([dict(op='new', values=[7]), dict(op='repeat', v=1, times=n),
                      dict(op='edit', v=2, l=0, r=n, a=0, b=1, c=2),
                      dict(op='at', v=3, i=n-1), dict(op='reverse', v=3, l=0, r=n),
                      dict(op='at', v=4, i=0), dict(op='at', v=4, i=n-1),
                      dict(op='at', v=2, i=n-1), dict(op='query', v=3, l=n-1, r=n)])
        self.assertEqual(actual[3], {'value': last})
        self.assertEqual(actual[5:8], [{'value': last}, {'value': 1}, {'value': 7}])
        self.assertEqual(actual[-1], stats([last]))

    def test_empty_versions_and_noop_ids(self):
        actual = run([dict(op='new', values=[]), dict(op='reverse', v=1, l=0, r=0),
                      dict(op='drop', v=1), dict(op='slice', v=2, l=0, r=0),
                      dict(op='query', v=3, l=0, r=0)])
        self.assertEqual(actual, [dict(v=1, n=0), dict(v=2, n=0), {'ok': True},
                                  dict(v=3, n=0), stats([])])

    def test_response_before_eof(self):
        proc = subprocess.Popen([sys.executable, str(ROOT/'loom.py')], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT)
        replies = queue.Queue()
        reader = threading.Thread(target=lambda: replies.put(proc.stdout.readline()), daemon=True)
        reader.start()
        try:
            proc.stdin.write(b'{"op":"new","values":[1]}\n')
            proc.stdin.flush()
            self.assertEqual(json.loads(replies.get(timeout=5)), {'v': 1, 'n': 1})
            proc.stdin.close()
            proc.wait(timeout=5)
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stderr.read(), b'')
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            reader.join(timeout=1)
            if not proc.stdin.closed:
                proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()


if __name__ == '__main__':
    unittest.main()
