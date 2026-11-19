import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_lock():
    lock=json.loads((ROOT/'LOCK.json').read_text(encoding='utf-8'))
    for name,digest in lock['files'].items():
        path=(ROOT/name).resolve()
        if ROOT not in path.parents or sha(path)!=digest:raise RuntimeError('frozen file changed: '+name)


def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result


class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
        ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
         'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]


memory_api=ctypes.WinDLL('psapi',use_last_error=True).GetProcessMemoryInfo
memory_api.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
memory_api.restype=wintypes.BOOL


def run_case(case,candidate,work):
    began=time.perf_counter()
    p=subprocess.Popen([sys.executable,'-I','-S','-B',str(HERE/'runner.py'),str(candidate)],cwd=work,
                       stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    lines=queue.Queue();errors=[];stop=threading.Event();stats={'peak':0,'memory_exceeded':False}
    def read_output():
        while True:
            line=p.stdout.readline(1048577)
            if not line:break
            lines.put(line)
            if len(line)>1048576:p.kill();break
        lines.put(None)
    def read_errors():errors.append(p.stderr.read())
    def sample_memory():
        c=Counters();c.cb=ctypes.sizeof(c)
        while not stop.is_set():
            if memory_api(int(p._handle),ctypes.byref(c),c.cb):
                stats['peak']=max(stats['peak'],c.PeakWorkingSetSize)
                if stats['peak']>512*1048576:
                    stats['memory_exceeded']=True
                    try:p.kill()
                    except OSError:pass
                    break
            stop.wait(.01)
    threads=[threading.Thread(target=f,daemon=True) for f in [read_output,read_errors,sample_memory]]
    for t in threads:t.start()
    def send_all():
        try:
            p.stdin.write(b''.join(json.dumps(c,separators=(',',':')).encode()+b'\n' for c in case['commands']))
            p.stdin.close()
        except (OSError,ValueError):pass
    writer=None;reason=None;difference=None;index=None;latency=[]
    try:
        if case['mode']=='batch':writer=threading.Thread(target=send_all,daemon=True);writer.start()
        for index,(command,want) in enumerate(zip(case['commands'],case['expected'])):
            started=time.perf_counter()
            if case['mode']=='interactive':
                p.stdin.write(json.dumps(command,separators=(',',':')).encode()+b'\n');p.stdin.flush()
            remaining=60-(time.perf_counter()-began)
            if remaining<=0:raise TimeoutError('60 second process limit')
            timeout=min(5,remaining) if case['mode']=='interactive' else remaining
            try:line=lines.get(timeout=timeout)
            except queue.Empty:raise TimeoutError('5 second response limit' if timeout==5 and case['mode']=='interactive' else '60 second process limit')
            latency.append(time.perf_counter()-started)
            if line is None:raise ValueError('early EOF')
            if not line.endswith(b'\n') or b'\r' in line or len(line)>1048576:raise ValueError('invalid line framing')
            actual=json.loads(line,object_pairs_hook=unique)
            if not same(actual,want):difference={'command_index':index,'expected':want,'actual':actual};raise ValueError('wrong response')
        if case['mode']=='interactive':p.stdin.close()
        p.wait(timeout=max(.001,60-(time.perf_counter()-began)))
    except Exception as exc:reason=type(exc).__name__+': '+str(exc)
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
        elif b''.join(errors):reason='stderr is not empty'
        elif lines.get(timeout=1) is not None:reason='extra stdout'
    if stats['memory_exceeded']:reason='512 MiB working set limit'
    result={'name':case['name'],'mode':case['mode'],'passed':reason is None,'seconds':time.perf_counter()-began,
            'peak_working_set_bytes':stats['peak'],'max_response_seconds':max(latency,default=0),
            'exit_code':p.returncode,'stderr_bytes':sum(map(len,errors)),'reason':reason}
    if reason:
        result['failed_at']=index
        if difference:result['difference']=difference
        result['stderr_preview']=b''.join(errors)[:2000].decode('utf-8',errors='replace')
    p.stdout.close();p.stderr.close();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--submission',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--case',default='')
    parser.add_argument('--stop-on-fail',action='store_true');args=parser.parse_args();verify_lock()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);work=out/'isolated';work.mkdir(exist_ok=True)
    candidate=work/'prism.py';shutil.copyfile(args.submission,candidate)
    cases=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((HERE/'fixtures').glob('*.json'))]
    if args.case:cases=[c for c in cases if args.case in c['name']]
    assert cases;started=time.perf_counter();results=[]
    for case in cases:
        result=run_case(case,candidate,work);result['visibility']=case['visibility'];results.append(result)
        print(('PASS ' if result['passed'] else 'FAIL ')+case['name']+' '+format(result['seconds'],'.4f')+'s',flush=True)
        (out/'progress.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if args.stop_on_fail and not result['passed']:break
    passed=sum(r['passed'] for r in results)
    hidden_passed=sum(r['passed'] for r in results if r['visibility']=='hidden')
    public_passed=sum(r['passed'] for r in results if r['visibility']=='public')
    report={'task':'PRISM','total':128,'hidden_total':112,'public_total':16,
            'hidden_passed':hidden_passed,'public_passed':public_passed,
            'selected':len(cases),'executed':len(results),'passed':passed,
            'complete_score':len(cases)==len(results)==128,'all_selected_passed':passed==len(cases),
            'submission_sha256':sha(candidate),'lock_sha256':sha(ROOT/'LOCK.json'),
            'seconds':time.perf_counter()-started,'results':results}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'CHECKED {passed}/{len(cases)} | HIDDEN {hidden_passed}/112 | PUBLIC {public_passed}/16',flush=True)
    return 0 if report['all_selected_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
