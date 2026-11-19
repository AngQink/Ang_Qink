import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((Path(__file__).parent/'fixtures.json').read_text(encoding='utf-8'))


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys()==b.keys() and all(same(a[key],b[key]) for key in a)
    if isinstance(a, list):
        return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b


def no_duplicates(pairs):
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValueError('duplicate JSON field')
    return data


def make_test(case):
    def test(self):
        launch = [sys.executable,'-I','-S','-B',str(ROOT/'prism.py')]
        with subprocess.Popen(launch,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as process:
            replies = queue.Queue()
            def read():
                for line in process.stdout:
                    replies.put(line)
                replies.put(None)
            thread = threading.Thread(target=read,daemon=True)
            thread.start()
            try:
                for cmd, want in zip(case['commands'],case['expected']):
                    process.stdin.write(json.dumps(cmd,separators=(',',':')).encode()+b'\n')
                    process.stdin.flush()
                    line = replies.get(timeout=5)
                    self.assertIsNotNone(line)
                    self.assertTrue(line.endswith(b'\n') and b'\r' not in line)
                    result = json.loads(line,object_pairs_hook=no_duplicates)
                    self.assertTrue(same(result,want), (cmd,result,want))
                process.stdin.close()
                self.assertEqual(process.wait(timeout=5),0)
                self.assertEqual(process.stderr.read(),b'')
                self.assertIsNone(replies.get(timeout=1))
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                thread.join(timeout=1)
    return test


class PublicCases(unittest.TestCase):
    pass


for case in CASES:
    setattr(PublicCases,'test_'+case['name'],make_test(case))


if __name__ == '__main__':
    unittest.main()
