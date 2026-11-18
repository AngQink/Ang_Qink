import hashlib
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import unittest

ROOT=Path(__file__).resolve().parents[1]
OK={'ok':True}


def rule(i,A,r,c=0,on=True):return dict(id=i,lhs=A,rhs=r,cost=c,enabled=on)
def init(n,rules,m=97):return dict(op='init',nonterminals=n,rules=rules,mod=m)
def query(word='',start=0,at=None):return dict(op='parse',start=start,word=word,at=at or [])
def digest(rid,*children):return hashlib.sha256(b'DERIVE1'+rid.to_bytes(4,'little')+bytes([len(children)])+b''.join(children)).digest()


def execute(commands):
    p=subprocess.run([sys.executable,'-B',str(ROOT/'ink.py')],input=''.join(json.dumps(c)+'\n' for c in commands).encode(),capture_output=True,timeout=8,cwd=ROOT)
    assert p.returncode==0 and not p.stderr,(p.returncode,p.stderr[-1000:])
    assert b'\r' not in p.stdout and p.stdout.endswith(b'\n')
    replies=[json.loads(x) for x in p.stdout.splitlines()];assert len(replies)==len(commands)
    return replies


class PublicTests(unittest.TestCase):
    def test_sample(self):
        c=[json.loads(x) for x in (ROOT/'samples/demo.ndjson').read_text().splitlines()]
        w=[json.loads(x) for x in (ROOT/'samples/demo.expected.ndjson').read_text().splitlines()]
        self.assertEqual(execute(c),w)
    def test_unproductive_cycle(self):self.assertEqual(execute([init(1,[rule(0,0,[0])]),query()])[-1],{'possible':False})
    def test_infinite_but_shortest_witness(self):
        r=execute([init(1,[rule(0,0,[0]),rule(7,0,['a'],3)]),query('a',at=[0,1])])[-1]
        self.assertEqual((r['cost'],r['infinite'],r['ways']),(3,True,None));self.assertEqual(r['witness'],dict(nodes=1,sha256=digest(7).hex(),at=[7,None]))
    def test_positive_cycle_not_optimal(self):
        r=execute([init(1,[rule(0,0,[0],1),rule(7,0,['a'],3)]),query('a')])[-1]
        self.assertEqual((r['cost'],r['infinite'],r['ways']),(3,False,1))
    def test_count_includes_longer_optimal_tree(self):
        r=execute([init(2,[rule(0,0,[1]),rule(1,1,['a']),rule(10,0,['a'])],2),query('a',at=[0])])[-1]
        self.assertTrue(r['possible']);self.assertEqual(r['ways'],0);self.assertFalse(r['infinite']);self.assertEqual(r['witness']['at'],[10])
    def test_node_count_precedes_rule_id(self):
        r=execute([init(2,[rule(0,0,[1,1]),rule(1,1,[]),rule(100,0,[])]),query(at=[0,1])])[-1]
        self.assertEqual(r['ways'],2);self.assertEqual(r['witness']['nodes'],1);self.assertEqual(r['witness']['at'],[100,None])
    def test_numeric_ids_and_array_order(self):
        r=execute([init(1,[rule(10,0,['a']),rule(2,0,['a'])]),query('a',at=[0])])[-1]
        self.assertEqual(r['ways'],2);self.assertEqual(r['witness']['at'],[2])
    def test_duplicate_children_are_independent(self):
        r=execute([init(2,[rule(9,0,[1,1]),rule(2,1,[]),rule(1,1,[])],6),query(at=[0,1,2,3])])[-1]
        self.assertEqual(r['ways'],4);self.assertEqual(r['witness'],dict(nodes=3,sha256=digest(9,digest(1),digest(1)).hex(),at=[9,1,1,None]))
    def test_catalan_witness_right_comb(self):
        r=execute([init(1,[rule(9,0,[0,0]),rule(2,0,['a'])]),query('aaa',at=list(range(6)))])[-1]
        self.assertEqual(r['ways'],2);self.assertEqual(r['witness']['at'],[9,2,9,2,2,None])
    def test_catalan_witness_left_comb(self):
        r=execute([init(1,[rule(1,0,[0,0]),rule(99,0,['a'])]),query('aaa',at=list(range(6)))])[-1]
        self.assertEqual(r['witness']['at'],[1,1,99,99,99,None])
    def test_zero_cycle_outside_goal(self):
        r=execute([init(2,[rule(1,0,['a']),rule(2,1,[1]),rule(3,1,[])]),query('a')])[-1]
        self.assertFalse(r['infinite']);self.assertEqual(r['ways'],1)
    def test_exact_wide_cost_and_unsigned_id_hash(self):
        v=(1<<63)-1;r=execute([init(2,[rule(0,0,[1,1],v),rule((1<<32)-1,1,['a'],v)]),query('aa')])[-1]
        self.assertEqual(r['cost'],3*v);self.assertEqual(r['witness']['sha256'],digest(0,digest((1<<32)-1),digest((1<<32)-1)).hex())
    def test_snapshot_disabled_weight(self):
        r=execute([init(1,[rule(1,0,['a'])]),dict(op='save',slot=31),dict(op='enable',id=1,value=False),dict(op='weight',id=1,cost=7),query('a'),dict(op='enable',id=1,value=True),query('a'),dict(op='load',slot=31),query('a')])
        self.assertEqual(r[4],{'possible':False});self.assertEqual(r[6]['cost'],7);self.assertEqual(r[8]['cost'],0)
    def test_compressed_epsilon_tree(self):
        rules=[rule(i,i,[i+1,i+1]) for i in range(23)]+[rule(23,23,[])]
        r=execute([init(24,rules),query(at=[0,(1<<24)-2,(1<<24)-1,1<<127])])[-1]
        self.assertEqual(r['witness']['nodes'],(1<<24)-1);self.assertEqual(r['witness']['at'],[0,23,None,None])
    def test_reply_before_eof(self):
        p=subprocess.Popen([sys.executable,'-B',str(ROOT/'ink.py')],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        q=queue.Queue()
        def read():
            for line in p.stdout:q.put(line)
        t=threading.Thread(target=read,daemon=True);t.start()
        try:
            p.stdin.write((json.dumps(init(1,[rule(9,0,['a'],3)]))+'\n').encode());p.stdin.flush();self.assertEqual(json.loads(q.get(timeout=5)),OK)
            p.stdin.write((json.dumps(query('a',at=[0]))+'\n').encode());p.stdin.flush();r=json.loads(q.get(timeout=5));self.assertEqual(r['witness']['at'],[9])
            p.stdin.close();p.wait(timeout=5);self.assertEqual(p.returncode,0);self.assertEqual(p.stderr.read(),b'')
        finally:
            if p.poll() is None:p.kill();p.wait()
            t.join(timeout=1)
            if not p.stdin.closed:p.stdin.close()
            p.stdout.close();p.stderr.close()


if __name__=='__main__':unittest.main()
