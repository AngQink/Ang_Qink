import ctypes
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time


def peak_bytes(proc):
    if os.name == 'nt':
        class Counters(ctypes.Structure):
            _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [
                (name, ctypes.c_size_t) for name in ('peak', 'working', 'qpp', 'qp', 'qnpp', 'qnp', 'pf', 'ppf')]
        value = Counters()
        value.cb = ctypes.sizeof(value)
        api = ctypes.windll.psapi.GetProcessMemoryInfo
        api.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        api.restype = ctypes.c_int
        if api(int(proc._handle), ctypes.byref(value), value.cb):
            return int(value.peak)
    else:
        try:
            for line in Path(f'/proc/{proc.pid}/status').read_text().splitlines():
                if line.startswith('VmHWM:'):
                    return int(line.split()[1])*1024
        except OSError:
            pass
    return 0


class Runner:
    def __init__(self, candidate):
        self.candidate = Path(candidate)
        self.metrics = []
        self.source_hash = hashlib.sha256(self.candidate.read_bytes()).hexdigest()

    def check_files(self):
        assert sorted(p.name for p in self.candidate.parent.iterdir()) == ['phase.py'], 'candidate created persistent files'
        assert hashlib.sha256(self.candidate.read_bytes()).hexdigest() == self.source_hash, 'candidate modified its source'

    def run(self, trace, timeout=30):
        commands, expected = trace['commands'], trace['expected']
        assert len(commands) <= 20000
        data = ''.join(json.dumps(c, separators=(',', ':'))+'\n' for c in commands).encode()
        start = time.perf_counter()
        proc = subprocess.Popen([sys.executable, '-B', str(self.candidate)], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.candidate.parent)
        done = threading.Event()
        peak, exceeded = [0], [False]

        def monitor():
            while not done.wait(.01):
                peak[0] = max(peak[0], peak_bytes(proc))
                if peak[0] > 512*2**20:
                    exceeded[0] = True
                    proc.kill()
                    return

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        try:
            try:
                stdout, stderr = proc.communicate(data, timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                raise AssertionError(f'exceeded {timeout} seconds')
        finally:
            done.set()
            thread.join()
            self.metrics.append(dict(elapsed_sec=round(time.perf_counter()-start, 4),
                                     peak_mib=round(peak[0]/2**20, 3), commands=len(commands)))
        assert not exceeded[0], f'exceeded 512 MiB ({peak[0]/2**20:.1f} MiB observed)'
        assert proc.returncode == 0, f'exit {proc.returncode}; stderr={stderr[-1200:]!r}'
        assert stderr == b'', f'nonempty stderr: {stderr[-1200:]!r}'
        self.check_files()
        assert b'\r' not in stdout, 'stdout must use LF'
        assert not stdout or stdout.endswith(b'\n'), 'last reply lacks LF'
        try:
            actual = [json.loads(line.decode('utf-8')) for line in stdout.split(b'\n')[:-1]]
        except (ValueError, UnicodeError) as exc:
            raise AssertionError('invalid UTF-8 NDJSON') from exc
        assert len(actual) == len(expected), f'{len(actual)} replies for {len(expected)} commands'
        for i, (want, got) in enumerate(zip(expected, actual)):
            assert same_json(want,got), (
                f'command {i}: {commands[i]!r}; expected {want!r}; got {got!r}')

    def interactive(self):
        start=time.perf_counter()
        proc=subprocess.Popen([sys.executable,'-B',str(self.candidate)],stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.candidate.parent)
        done=threading.Event();peak=[0];exceeded=[False]
        def monitor():
            while not done.wait(.01):
                peak[0]=max(peak[0],peak_bytes(proc))
                if peak[0]>512*2**20:
                    exceeded[0]=True;proc.kill();return
        memory_thread=threading.Thread(target=monitor,daemon=True);memory_thread.start()
        responses=queue.Queue()
        def read():
            for line in proc.stdout:responses.put(line)
            responses.put(None)
        thread=threading.Thread(target=read,daemon=True);thread.start()
        try:
            commands=[dict(op='init',n=2,linear=[1,0],edges=[],constant=0),dict(op='save',slot=0),dict(op='ask',a=[],b=[])]
            expected=[{'ok':True},{'ok':True},{'possible':True,'free':2,'first':'00','amplitude':{'zero':False,'power':3,'phase':1}}]
            last=None
            for cmd,want in zip(commands,expected):
                proc.stdin.write((json.dumps(cmd)+'\n').encode());proc.stdin.flush()
                line=responses.get(timeout=5)
                assert line is not None and same_json(want,json.loads(line))
                last=want
            cmd=dict(op='phase',u=last['amplitude']['phase']%2,delta=2)
            proc.stdin.write((json.dumps(cmd)+'\n').encode());proc.stdin.flush()
            assert same_json({'ok':True},json.loads(responses.get(timeout=5)))
            cmd=dict(op='ask',a=[],b=[])
            proc.stdin.write((json.dumps(cmd)+'\n').encode());proc.stdin.flush()
            assert same_json({'possible':True,'free':2,'first':'00','amplitude':{'zero':True}},json.loads(responses.get(timeout=5)))
            cmd=dict(op='overlap',left=0,right=0,a=['3'],b=[1])
            proc.stdin.write((json.dumps(cmd)+'\n').encode());proc.stdin.flush()
            projected=json.loads(responses.get(timeout=5))
            assert same_json({'possible':True,'free':1,'first':'01','amplitude':{'zero':False,'power':2,'phase':0}},projected)
            cmd=dict(op='value',bits=projected['first'])
            proc.stdin.write((json.dumps(cmd)+'\n').encode());proc.stdin.flush()
            assert same_json({'phase':2},json.loads(responses.get(timeout=5)))
            proc.stdin.close();proc.wait(timeout=5)
            assert proc.returncode==0 and proc.stderr.read()==b''
            assert not exceeded[0], 'exceeded 512 MiB'
            thread.join(timeout=1)
            extra=[]
            while not responses.empty():extra.append(responses.get_nowait())
            assert extra==[None], 'extra replies after the adaptive conversation'
            self.check_files()
        finally:
            done.set();memory_thread.join()
            if proc.poll() is None:proc.kill();proc.wait(timeout=5)
            thread.join(timeout=1)
            if not proc.stdin.closed:proc.stdin.close()
            proc.stdout.close();proc.stderr.close()
            self.metrics.append(dict(elapsed_sec=round(time.perf_counter()-start,4),peak_mib=round(peak[0]/2**20,3),commands=7,interactive=True))


def same_json(expected,actual):
    if type(expected) is not type(actual):return False
    if isinstance(expected,dict):
        return expected.keys()==actual.keys() and all(same_json(v,actual[k]) for k,v in expected.items())
    if isinstance(expected,list):
        return len(expected)==len(actual) and all(same_json(a,b) for a,b in zip(expected,actual))
    return expected==actual

