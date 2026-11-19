import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
OK={'ok':True}


def init(n,linear=None,edges=None,c=0):return dict(op='init',n=n,linear=linear or [0]*n,edges=edges or [],constant=c)
def ask(a=None,b=None):return dict(op='ask',a=a or [],b=b or [])
def amp(k,p):return {'zero':False,'power':k,'phase':p}
def result(free,first,amplitude):return dict(possible=True,free=free,first=first,amplitude=amplitude)


def execute(commands):
    p=subprocess.run([sys.executable,'-B',str(ROOT/'phase.py')],cwd=ROOT,input=''.join(json.dumps(c)+'\n' for c in commands).encode(),capture_output=True,timeout=8)
    assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:])
    assert b'\r' not in p.stdout and p.stdout.endswith(b'\n')
    replies=[json.loads(s) for s in p.stdout.splitlines()];assert len(replies)==len(commands)
    return replies


class PublicTests(unittest.TestCase):
    def test_sample(self):
        c=[json.loads(s) for s in (ROOT/'samples/demo.ndjson').read_text().splitlines()]
        want=[json.loads(s) for s in (ROOT/'samples/demo.expected.ndjson').read_text().splitlines()]
        self.assertEqual(execute(c),want)
    def test_odd_phase(self):self.assertEqual(execute([init(1,[1]),ask()])[-1],result(1,'0',amp(1,1)))
    def test_cancellation_and_infeasible_are_different(self):
        r=execute([init(1,[2]),ask(),ask(['0'],[1])]);self.assertEqual(r[1],result(1,'0',{'zero':True}));self.assertEqual(r[2],{'possible':False})
    def test_edge_interference(self):self.assertEqual(execute([init(2,edges=[[0,1]]),ask()])[-1],result(2,'00',amp(2,0)))
    def test_global_phase(self):
        r=execute([init(1,c=1),ask(),dict(op='global',delta=-1),ask()]);self.assertEqual(r[1],result(1,'0',amp(2,2)));self.assertEqual(r[-1],result(1,'0',amp(2,0)))
    def test_xor_odd_linear_creates_quadratic_term(self):
        r=execute([init(2,[1,0]),dict(op='xor',dst=0,src=1),dict(op='value',bits='11'),ask()]);self.assertEqual(r[2],{'phase':0});self.assertEqual(r[-1],result(2,'00',amp(3,1)))
    def test_flip(self):
        r=execute([init(1,[1]),dict(op='flip',u=0),dict(op='value',bits='0'),ask()]);self.assertEqual(r[2],{'phase':1});self.assertEqual(r[-1],result(1,'0',amp(1,1)))
    def test_overlap_conjugation(self):
        r=execute([init(1),dict(op='save',slot=0),dict(op='phase',u=0,delta=1),dict(op='save',slot=1),dict(op='overlap',left=1,right=0,a=[],b=[]),dict(op='overlap',left=0,right=1,a=[],b=[])]);self.assertEqual(r[-2],result(1,'0',amp(1,1)));self.assertEqual(r[-1],result(1,'0',amp(1,7)))
    def test_zero_variables(self):
        r=execute([init(0,c=3),ask(),dict(op='value',bits='')]);self.assertEqual(r[1],result(0,'',amp(0,6)));self.assertEqual(r[2],{'phase':3})
    def test_lexicographic_bit_order(self):self.assertEqual(execute([init(2),ask(['3'],[1])])[-1],result(1,'01',amp(2,0)))
    def test_snapshot_and_delta_boundaries(self):
        r=execute([init(1,[1]),dict(op='save',slot=63),dict(op='phase',u=0,delta=1),ask(),dict(op='load',slot=63),dict(op='global',delta=-(1<<63)),ask(),dict(op='global',delta=(1<<63)-1),dict(op='value',bits='1')]);self.assertEqual(r[3]['amplitude'],{'zero':True});self.assertEqual(r[6],result(1,'0',amp(1,1)));self.assertEqual(r[-1],{'phase':0})
    def test_swap(self):
        r=execute([init(2,[1,2]),dict(op='swap',u=0,v=1),dict(op='value',bits='10'),dict(op='value',bits='01')]);self.assertEqual(r[-2:], [{'phase':2},{'phase':1}])
    def test_reply_before_eof(self):
        p=subprocess.Popen([sys.executable,'-B',str(ROOT/'phase.py')],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        q=queue.Queue()
        def read():
            for line in p.stdout:q.put(line)
        reader=threading.Thread(target=read,daemon=True);reader.start()
        try:
            for c,want in [(init(1,[1]),OK),(ask(),result(1,'0',amp(1,1)))]:
                p.stdin.write((json.dumps(c)+'\n').encode());p.stdin.flush();self.assertEqual(json.loads(q.get(timeout=5)),want)
            p.stdin.close();p.wait(timeout=5);self.assertEqual(p.returncode,0);self.assertEqual(p.stderr.read(),b'')
        finally:
            if p.poll() is None:p.kill();p.wait()
            reader.join(timeout=1)
            if not p.stdin.closed:p.stdin.close()
            p.stdout.close();p.stderr.close()


if __name__=='__main__':unittest.main()
