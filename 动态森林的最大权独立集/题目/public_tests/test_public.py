import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]


def run(commands):
    result=subprocess.run([sys.executable,'-B',str(ROOT/'forest.py')],
                          input=''.join(json.dumps(c)+'\n' for c in commands).encode(),
                          capture_output=True,timeout=8,cwd=ROOT)
    assert result.returncode==0 and result.stderr==b'', (result.returncode,result.stderr)
    assert b'\r' not in result.stdout and result.stdout.endswith(b'\n')
    replies=[json.loads(line) for line in result.stdout.splitlines()]
    assert len(replies)==len(commands)
    return replies


def init(weights,edges,mod):
    return dict(op='init',weights=weights,edges=edges,mod=mod)


class PublicTests(unittest.TestCase):
    def test_sample(self):
        commands=[json.loads(x) for x in (ROOT/'samples/demo.ndjson').read_text(encoding='utf-8').splitlines()]
        expected=[json.loads(x) for x in (ROOT/'samples/demo.expected.ndjson').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(run(commands),expected)

    def test_zero_count_remains_possible(self):
        replies=run([init([0,0,0],[[0,1],[0,2]],4),dict(op='ask',u=0),
                     dict(op='pair',u=0,v=0,su=0,sv=0),dict(op='pair',u=0,v=0,su=0,sv=1)])
        self.assertEqual(replies[1],{'n':3,'best':{'weight':0,'ways':1},
                                     'out':{'weight':0,'ways':0},'in':{'weight':0,'ways':1}})
        self.assertEqual(replies[2],dict(connected=True,possible=True,weight=0,ways=0))
        self.assertEqual(replies[3],dict(connected=True,possible=False))

    def test_nonunits_under_different_queries(self):
        commands=[init([-1,0,0,0],[[0,1],[0,2],[2,3]],6)]
        commands.extend(dict(op='ask',u=u) for u in [0,1,2,3,0,2,1,3])
        for reply in run(commands)[1:]:
            self.assertEqual(reply['n'],4)
            self.assertEqual(reply['best'],dict(weight=0,ways=0))

    def test_pair_optimizes_off_path_branches(self):
        replies=run([init([4,1,4,100],[[0,1],[1,2],[1,3]],12),
                     dict(op='pair',u=0,v=2,su=1,sv=1),
                     dict(op='pair',u=1,v=3,su=1,sv=1)])
        self.assertEqual(replies[1],dict(connected=True,possible=True,weight=108,ways=1))
        self.assertEqual(replies[2],dict(connected=True,possible=False))

    def test_cut_link_changes_components(self):
        replies=run([init([4,1,5,2],[[0,1],[1,2],[2,3]],1000),
                     dict(op='cut',u=2,v=1),dict(op='ask',u=0),
                     dict(op='pair',u=0,v=3,su=1,sv=1),dict(op='link',u=3,v=0),
                     dict(op='pair',u=0,v=2,su=1,sv=1)])
        self.assertEqual(replies[2],{'n':2,'best':dict(weight=4,ways=1),
                                     'out':dict(weight=1,ways=1),'in':dict(weight=4,ways=1)})
        self.assertEqual(replies[3],dict(connected=False))
        self.assertEqual(replies[-1],dict(connected=True,possible=True,weight=9,ways=1))

    def test_exact_large_integer_scores(self):
        maximum=2**63-1
        replies=run([init([maximum,2**62-1,2**62-1],[[0,1],[0,2]],101),dict(op='ask',u=0),
                     dict(op='set',u=1,w=maximum),dict(op='set',u=2,w=maximum),dict(op='ask',u=0)])
        self.assertEqual(replies[1]['best'],dict(weight=maximum,ways=1))
        self.assertEqual(replies[1]['out'],dict(weight=maximum-1,ways=1))
        self.assertEqual(replies[-1]['best'],dict(weight=2*maximum,ways=1))

    def test_forced_negative_and_impossible(self):
        minimum=-2**63
        replies=run([init([minimum,-1,minimum],[[0,1],[1,2]],6),
                     dict(op='pair',u=0,v=2,su=1,sv=1),dict(op='ask',u=0)])
        self.assertEqual(replies[1],dict(connected=True,possible=True,weight=2*minimum,ways=1))
        self.assertEqual(replies[2]['best'],dict(weight=0,ways=1))

    def test_reply_before_eof(self):
        proc=subprocess.Popen([sys.executable,'-B',str(ROOT/'forest.py')],stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=ROOT)
        responses=queue.Queue()
        def read():
            for line in proc.stdout:responses.put(line)
        thread=threading.Thread(target=read,daemon=True);thread.start()
        try:
            proc.stdin.write(b'{"op":"init","weights":[0],"edges":[],"mod":4}\n');proc.stdin.flush()
            self.assertEqual(json.loads(responses.get(timeout=5)),dict(ok=True))
            proc.stdin.write(b'{"op":"ask","u":0}\n');proc.stdin.flush()
            self.assertEqual(json.loads(responses.get(timeout=5)),{'n':1,'best':dict(weight=0,ways=2),
                              'out':dict(weight=0,ways=1),'in':dict(weight=0,ways=1)})
            proc.stdin.close();proc.wait(timeout=5)
            self.assertEqual(proc.returncode,0)
            self.assertEqual(proc.stderr.read(),b'')
        finally:
            if proc.poll() is None:proc.kill();proc.wait(timeout=5)
            thread.join(timeout=1)
            if not proc.stdin.closed:proc.stdin.close()
            proc.stdout.close();proc.stderr.close()


if __name__=='__main__':unittest.main()
