import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_lock():
    lock=json.loads((ROOT/'LOCK.json').read_text(encoding='utf-8'))
    for relative,digest in lock['files'].items():
        path=(ROOT/relative).resolve()
        if ROOT not in path.parents or sha(path)!=digest:raise RuntimeError('frozen file changed: '+relative)


def same(got,want):
    if type(got) is not type(want):return False
    if isinstance(want,dict):return got.keys()==want.keys() and all(same(got[k],want[k]) for k in want)
    if isinstance(want,list):return len(got)==len(want) and all(same(a,b) for a,b in zip(got,want))
    return got==want


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result


class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
        (field,ctypes.c_size_t) for field in ['PeakWorkingSetSize','WorkingSetSize',
        'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
        'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]


memory_api=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
memory_api.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
memory_api.restype=wintypes.BOOL


def run(case,candidate,work):
    began=time.perf_counter()
    p=subprocess.Popen([sys.executable,'-I','-S','-B',str(HERE/'runner.py'),str(candidate)],
                       cwd=work,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output=queue.Queue();stop=threading.Event();stats={'peak':0,'memory_exceeded':False};stderr=[];raw=[]
    def reader():
        while True:
            line=p.stdout.readline(1_048_577)
            if not line:break
            output.put(line)
            if len(line)>1_048_576:p.kill();break
        output.put(None)
    def read_error():stderr.append(p.stderr.read())
    def memory():
        counters=Counters();counters.cb=ctypes.sizeof(Counters)
        while not stop.is_set():
            if memory_api(int(p._handle),ctypes.byref(counters),counters.cb):
                stats['peak']=max(stats['peak'],counters.PeakWorkingSetSize)
                if stats['peak']>512*1024*1024:
                    stats['memory_exceeded']=True
                    try:p.kill()
                    except OSError:pass
                    break
            stop.wait(.01)
    threads=[threading.Thread(target=f,daemon=True) for f in [reader,read_error,memory]]
    for t in threads:t.start()
    reason=None;failed_at=None;first_difference=None;latencies=[];writer=None
    def write_all():
        try:
            p.stdin.write(b''.join(json.dumps(c,separators=(',',':')).encode()+b'\n' for c in case['commands']))
            p.stdin.close()
        except (OSError,ValueError):pass
    try:
        if case['mode']=='batch':writer=threading.Thread(target=write_all,daemon=True);writer.start()
        for i,(command,want) in enumerate(zip(case['commands'],case['expected'])):
            sent=time.perf_counter()
            if case['mode']=='interactive':
                p.stdin.write(json.dumps(command,separators=(',',':')).encode()+b'\n');p.stdin.flush()
            remaining=60-(time.perf_counter()-began)
            if remaining<=0:raise TimeoutError('60 second process limit')
            timeout=min(5,remaining) if case['mode']=='interactive' else remaining
            try:line=output.get(timeout=timeout)
            except queue.Empty:raise TimeoutError('5 second response limit' if case['mode']=='interactive' and timeout==5 else '60 second process limit')
            latencies.append(time.perf_counter()-sent)
            if line is None:raise ValueError('EOF before all responses')
            raw.append(line)
            if not line.endswith(b'\n') or b'\r' in line or len(line)>1_048_576:raise ValueError('invalid line framing')
            got=json.loads(line,object_pairs_hook=unique_object)
            if not same(got,want):
                first_difference={'command_index':i,'expected':want,'actual':got}
                raise ValueError('wrong response')
        if case['mode']=='interactive':p.stdin.close()
        p.wait(timeout=max(.001,60-(time.perf_counter()-began)))
    except Exception as exc:
        reason=type(exc).__name__+': '+str(exc);failed_at=len(raw)-1 if raw else 0
    finally:
        if p.poll() is None:p.kill();p.wait()
        stop.set()
        for t in threads:t.join(timeout=2)
        if writer:writer.join(timeout=2)
        try:
            if not p.stdin.closed:p.stdin.close()
        except OSError:pass
    if reason is None:
        if p.returncode!=0:reason='nonzero exit code'
        elif b''.join(stderr):reason='stderr is not empty'
        elif output.get(timeout=1) is not None:reason='extra stdout'
    if stats['memory_exceeded']:reason='512 MiB working set limit'
    result={'name':case['name'],'mode':case['mode'],'passed':reason is None,
            'seconds':time.perf_counter()-began,'peak_working_set_bytes':stats['peak'],
            'max_response_seconds':max(latencies,default=0),'exit_code':p.returncode,
            'stderr_bytes':sum(len(x) for x in stderr),'reason':reason}
    if reason is not None:
        result['failed_at']=failed_at
        if first_difference:result['difference']=first_difference
        result['stderr_preview']=b''.join(stderr)[:2000].decode('utf-8',errors='replace')
    p.stdout.close();p.stderr.close()
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--submission',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--case',default='')
    parser.add_argument('--stop-on-fail',action='store_true')
    args=parser.parse_args();verify_lock()
    original=args.submission.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    work=out/'isolated';work.mkdir(exist_ok=True);candidate=work/'mirror.py'
    shutil.copyfile(original,candidate)
    cases=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((HERE/'fixtures').glob('*.json'))]
    if args.case:cases=[c for c in cases if args.case in c['name']]
    assert cases,'no matching frozen cases'
    started=time.perf_counter();results=[]
    for case in cases:
        result=run(case,candidate,work);results.append(result)
        print(('PASS ' if result['passed'] else 'FAIL ')+result['name']+' '+format(result['seconds'],'.4f')+'s',flush=True)
        (out/'progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if args.stop_on_fail and not result['passed']:break
    passed=sum(r['passed'] for r in results)
    report={'task':'ECLIPSE MIRROR','official_total':96,'selected':len(cases),'executed':len(results),
            'passed':passed,'all_selected_passed':passed==len(cases),'reward':int(len(cases)==96 and passed==96),
            'submission_sha256':sha(candidate),'lock_sha256':sha(ROOT/'LOCK.json'),
            'seconds':time.perf_counter()-started,'results':results}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'SCORE {passed}/{len(cases)} reward={report["reward"]}',flush=True)
    return 0 if report['all_selected_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
