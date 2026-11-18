import json
import subprocess
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def execute(cmds):
    p = subprocess.run([sys.executable, '-B', str(ROOT / 'ink.py')],
        input=''.join(json.dumps(c) + '\n' for c in cmds).encode(),
        capture_output=True, timeout=8, cwd=ROOT)
    assert p.returncode == 0 and not p.stderr, (p.returncode, p.stderr[-1000:])
    return [json.loads(x) for x in p.stdout.splitlines()]


class MinwaysTests(unittest.TestCase):
    def test_duplicate_children(self):
        reps = execute([
            {'op': 'init', 'nonterminals': 2, 'mod': 6, 'rules': [
                {'id': 9, 'lhs': 0, 'rhs': [1, 1], 'cost': 3, 'enabled': True},
                {'id': 2, 'lhs': 1, 'rhs': [], 'cost': 0, 'enabled': True},
                {'id': 1, 'lhs': 1, 'rhs': [], 'cost': 0, 'enabled': True}]},
            {'op': 'minways', 'start': 0, 'word': ''},
            {'op': 'parse', 'start': 0, 'word': '', 'at': [0, 1, 2]},
        ])
        assert reps[1] == {'possible': True, 'nodes': 3, 'ways': 4}
        assert reps[2]['witness']['nodes'] == 3
