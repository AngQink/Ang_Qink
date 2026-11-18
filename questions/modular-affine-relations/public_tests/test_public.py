import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]


def execute(commands):
    data=''.join(json.dumps(c,separators=(',',':'))+'\n' for c in commands).encode()
    p=subprocess.run([sys.executable,'-B',str(ROOT/'circuit.py')],input=data,capture_output=True,timeout=8,cwd=ROOT)
    assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1200:])
    assert b'\r' not in p.stdout and p.stdout.endswith(b'\n')
    replies=[json.loads(line) for line in p.stdout.splitlines()]
    assert len(replies)==len(commands)
    return replies


def init(m):return dict(op='init',mod=m)
def make(dst,d,a=(),b=()):return dict(op='make',dst=dst,dim=d,a=list(a),b=list(b))
def ask(s):return dict(op='ask',src=s)
def answer(d,n,x):return dict(dim=d,count=n,first=x)


class PublicTests(unittest.TestCase):
    def test_sample(self):
        commands=[json.loads(s) for s in (ROOT/'samples/demo.ndjson').read_text().splitlines()]
        want=[json.loads(s) for s in (ROOT/'samples/demo.expected.ndjson').read_text().splitlines()]
        self.assertEqual(execute(commands),want)

    def test_nonunit(self):
        r=execute([init(12),make(0,1,[[6]],[6]),ask(0)])
        self.assertEqual(r[-1],answer(1,6,[1]))

    def test_image_deduplicates(self):
        r=execute([init(12),make(0,1,[[6]],[6]),dict(op='map',src=0,dst=1,a=[[6]],b=[0]),ask(1)])
        self.assertEqual(r[-1],answer(1,1,[6]))

    def test_lexicographic(self):
        r=execute([init(6),make(0,2,[[2,3]],[1]),ask(0)])
        self.assertEqual(r[-1],answer(2,6,[2,1]))

    def test_annihilator(self):
        r=execute([init(4),make(0,1),dict(op='map',src=0,dst=1,a=[[2],[1]],b=[0,0]),ask(1),dict(op='has',src=1,point=[0,2])])
        self.assertEqual(r[-2],answer(2,4,[0,0]));self.assertEqual(r[-1],dict(contains=True))

    def test_same_slot_independent(self):
        r=execute([init(6),make(0,1),dict(op='join',left=0,right=0,dst=1,ties=[],keep=[0,1]),ask(1)])
        self.assertEqual(r[-1],answer(2,36,[0,0]))

    def test_hidden_multiplicity(self):
        r=execute([init(6),make(0,2,[[2,-2]],[0]),dict(op='join',left=0,right=0,dst=0,ties=[[1,0]],keep=[0,3]),ask(0)])
        self.assertEqual(r[-1],answer(2,12,[0,0]))

    def test_alias_and_copy(self):
        r=execute([init(6),make(0,1),dict(op='copy',src=0,dst=1),dict(op='pin',src=0,dst=0,a=[[1]],b=[5]),ask(0),ask(1)])
        self.assertEqual(r[-2],answer(1,1,[5]));self.assertEqual(r[-1],answer(1,6,[0]))

    def test_zero_dimension(self):
        r=execute([init(8),make(0,0),ask(0),make(1,0,[[]],[1]),ask(1)])
        self.assertEqual(r[2],answer(0,1,[]));self.assertEqual(r[-1],answer(0,0,None))

    def test_empty_meet(self):
        r=execute([init(12),make(0,1,[[2]],[2]),make(1,1,[[2]],[0]),dict(op='meet',left=0,right=1,dst=2),ask(2)])
        self.assertEqual(r[-1],answer(1,0,None))

    def test_negative_coefficients(self):
        r=execute([init(12),make(0,1,[[-4]],[-8]),ask(0),dict(op='map',src=0,dst=0,a=[[-1]],b=[-1]),ask(0)])
        self.assertEqual(r[2],answer(1,4,[2]));self.assertEqual(r[-1],answer(1,4,[0]))

    def test_large_integer_count(self):
        r=execute([init(1<<100),make(0,1,[[1<<70]],[1<<75]),ask(0)])
        self.assertEqual(r[-1],answer(1,1<<70,[32]))

    def test_probe_duplicate_coordinates(self):
        r=execute([init(6),make(0,2),dict(op='probe',src=0,a=[[1,0]],b=[5],keep=[1,1]),ask(0)])
        self.assertEqual(r[2],answer(2,6,[0,0]));self.assertEqual(r[-1],answer(2,36,[0,0]))

    def test_online_before_eof(self):
        p=subprocess.Popen([sys.executable,'-B',str(ROOT/'circuit.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=ROOT)
        q=queue.Queue()
        def read():
            for line in p.stdout:q.put(line)
        thread=threading.Thread(target=read,daemon=True);thread.start()
        try:
            commands=[init(6),make(0,2,[[2,3]],[1]),ask(0)]
            expected=[dict(ok=True),dict(ok=True),answer(2,6,[2,1])]
            for c,want in zip(commands,expected):
                p.stdin.write((json.dumps(c)+'\n').encode());p.stdin.flush()
                self.assertEqual(json.loads(q.get(timeout=5)),want)
            p.stdin.close();p.wait(timeout=5)
            self.assertEqual(p.returncode,0);self.assertEqual(p.stderr.read(),b'')
        finally:
            if p.poll() is None:p.kill();p.wait(timeout=5)
            thread.join(timeout=1)
            if not p.stdin.closed:p.stdin.close()
            p.stdout.close();p.stderr.close()


if __name__=='__main__':unittest.main()
