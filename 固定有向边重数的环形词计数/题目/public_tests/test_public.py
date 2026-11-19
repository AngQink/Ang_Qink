import json
import queue
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((Path(__file__).parent/'fixtures.json').read_text(encoding='utf-8'))


def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b


def run_case(case):
    p=subprocess.Popen([sys.executable,'-I','-S','-B',str(ROOT/'euler.py')],cwd=ROOT,
                       stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    lines=queue.Queue()
    def read():
        for line in p.stdout:lines.put(line)
        lines.put(None)
    t=threading.Thread(target=read,daemon=True);t.start();start=time.perf_counter()
    try:
        for command,want in zip(case['commands'],case['expected']):
            p.stdin.write(json.dumps(command,separators=(',',':')).encode()+b'\n');p.stdin.flush()
            line=lines.get(timeout=min(5,60-(time.perf_counter()-start)))
            assert line is not None and line.endswith(b'\n') and b'\r' not in line
            actual=json.loads(line);assert same(actual,want),(command,actual,want)
        p.stdin.close();p.wait(timeout=max(.01,60-(time.perf_counter()-start)));t.join(timeout=1)
        assert p.returncode==0 and p.stderr.read()==b'' and lines.get(timeout=1) is None
    finally:
        if p.poll() is None:p.kill();p.wait()
        t.join(timeout=1)
        if not p.stdin.closed:p.stdin.close()
        p.stdout.close();p.stderr.close()


class PublicTests(unittest.TestCase):pass


for case in CASES:
    def test(self,case=case):run_case(case)
    setattr(PublicTests,'test_'+case['name'],test)


if __name__=='__main__':unittest.main()
