import json
import subprocess
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SAMPLES=sorted(p for p in (ROOT/'samples').glob('sample_*.ndjson') if not p.name.endswith('.expected.ndjson'))
class PublicTests(unittest.TestCase):pass
def make_test(inp):
    exp=inp.with_name(inp.stem+'.expected.ndjson')
    def test(self):
        p=subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'hex.py')],input=inp.read_bytes(),capture_output=True,timeout=60,cwd=ROOT)
        self.assertEqual(p.returncode,0,p.stderr[-500:])
        self.assertEqual(p.stderr,b'')
        self.assertEqual([json.loads(x) for x in p.stdout.splitlines()],[json.loads(x) for x in exp.read_bytes().splitlines()])
    return test
for i,s in enumerate(SAMPLES):setattr(PublicTests,'test_sample_%02d'%i,make_test(s))
if __name__=='__main__':unittest.main()
