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
        assert sorted(p.name for p in self.candidate.parent.iterdir()) == ['loom.py'], 'candidate created persistent files'
        assert hashlib.sha256(self.candidate.read_bytes()).hexdigest() == self.source_hash, 'candidate modified its source'

    def run(self, trace, timeout=20):
        commands, expected = trace.commands, trace.expected
        assert len(commands) <= 60000
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
            assert got == want and all(type(v) is type(want[k]) for k, v in got.items()), (
                f'command {i}: {commands[i]!r}; expected {want!r}; got {got!r}')

    def interactive(self):
        from models import ListModel
        proc = subprocess.Popen([sys.executable, '-B', str(self.candidate)], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.candidate.parent)
        replies = queue.Queue()

        def read():
            for line in proc.stdout:
                replies.put(line)
            replies.put(None)

        thread = threading.Thread(target=read, daemon=True)
        thread.start()
        model = ListModel()
        try:
            commands = [dict(op='new', values=[3, 1, 4, 1, 5]), dict(op='concat', left=1, right=1),
                        dict(op='edit', v=2, l=1, r=9, a=-7, b=11, c=13),
                        dict(op='query', v=3, l=0, r=10)]
            for cmd in commands:
                expected = model.execute(cmd)
                proc.stdin.write((json.dumps(cmd)+'\n').encode())
                proc.stdin.flush()
                try:
                    line = replies.get(timeout=5)
                except queue.Empty as exc:
                    raise AssertionError('did not answer before EOF') from exc
                assert line is not None and json.loads(line) == expected
            # The next coordinate genuinely depends on the previous response.
            index = (expected['moment']+expected['forward']) % 10
            cmd = dict(op='at', v=3, i=index)
            proc.stdin.write((json.dumps(cmd)+'\n').encode())
            proc.stdin.flush()
            assert json.loads(replies.get(timeout=5)) == model.execute(cmd)
            proc.stdin.close()
            proc.wait(timeout=5)
            assert proc.returncode == 0
            assert proc.stderr.read() == b''
            self.check_files()
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            thread.join(timeout=1)
            if not proc.stdin.closed:
                proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()
