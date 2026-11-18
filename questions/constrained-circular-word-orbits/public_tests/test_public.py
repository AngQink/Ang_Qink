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


def same(got,want):
    if type(got) is not type(want):return False
    if isinstance(want,dict):return got.keys()==want.keys() and all(same(got[k],want[k]) for k in want)
    if isinstance(want,list):return len(got)==len(want) and all(same(a,b) for a,b in zip(got,want))
    return got==want


def run_case(case):
    p=subprocess.Popen([sys.executable,'-I','-S','-B',str(ROOT/'mirror.py')],cwd=ROOT,
                       stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output=queue.Queue()
    def read():
        for line in p.stdout:output.put(line)
        output.put(None)
    reader=threading.Thread(target=read,daemon=True);reader.start()
    began=time.perf_counter()
    try:
        for command,want in zip(case['commands'],case['expected']):
            p.stdin.write(json.dumps(command,separators=(',',':')).encode()+b'\n');p.stdin.flush()
            line=output.get(timeout=min(5,60-(time.perf_counter()-began)))
            assert line is not None and line.endswith(b'\n') and b'\r' not in line,line
            got=json.loads(line)
            assert same(got,want),(command,got,want)
        p.stdin.close();p.wait(timeout=max(.1,60-(time.perf_counter()-began)))
        reader.join(timeout=1)
        assert p.returncode==0 and p.stderr.read()==b''
        assert output.get(timeout=1) is None,'extra output'
    finally:
        if p.poll() is None:p.kill();p.wait()
        reader.join(timeout=1)
        if not p.stdin.closed:p.stdin.close()
        p.stdout.close();p.stderr.close()


class PublicTests(unittest.TestCase):pass


for case in CASES:
    def test(self,case=case):run_case(case)
    setattr(PublicTests,'test_'+case['name'],test)


if __name__=='__main__':unittest.main()
