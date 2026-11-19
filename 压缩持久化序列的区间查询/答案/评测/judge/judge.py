import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time
import traceback

from cases import CASES
from runner import Runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True, help='loom.py file or containing directory')
    parser.add_argument('--out', required=True, help='new report directory')
    parser.add_argument('--case', help='diagnostic substring filter; cannot earn official success')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out/'reward.txt').write_text('0\n', encoding='ascii')
    scratch = Path(tempfile.mkdtemp(prefix='scratch-', dir=out))
    report = dict(reward=0, full_suite=not bool(args.case), cases=[])
    try:
        source = Path(args.candidate).resolve(strict=True)
        if source.is_dir():
            source = source/'loom.py'
        raw = source.read_bytes()
        report.update(candidate=str(source), sha256=hashlib.sha256(raw).hexdigest())
        target = scratch/'loom.py'
        target.write_bytes(raw)
        runner = Runner(target)
        selected = [(name, build) for name, build in CASES if not args.case or args.case in name]
        if not args.case or args.case in 'interactive_adaptive_before_eof':
            selected.append(('interactive_adaptive_before_eof', None))
        assert selected, 'no matching case'
        for name, build in selected:
            started = time.perf_counter()
            prior = len(runner.metrics)
            try:
                if build is None:
                    runner.interactive()
                else:
                    trace = build()
                    runner.run(trace)
                status, error = 'PASS', None
            except Exception as exc:
                status, error = 'FAIL', f'{type(exc).__name__}: {exc}'[:2500]
            result = dict(name=name, status=status, total_sec=round(time.perf_counter()-started, 4),
                          processes=runner.metrics[prior:])
            if error:
                result['error'] = error
            report['cases'].append(result)
            print(f'{status:4} {name}' + (f' -- {error[:150]}' if error else ''), flush=True)
        report['passed'] = sum(x['status'] == 'PASS' for x in report['cases'])
        report['total'] = len(report['cases'])
        report['reward'] = int(not args.case and report['total'] > 0 and report['passed'] == report['total'])
        print(f"\n{report['passed']}/{report['total']}; reward={report['reward']}")
    except Exception as exc:
        report['infrastructure_error'] = f'{type(exc).__name__}: {exc}'
        traceback.print_exc()
    finally:
        (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        (out/'reward.txt').write_text(str(report['reward'])+'\n', encoding='ascii')
        assert scratch.resolve().parent == out and scratch.name.startswith('scratch-')
        if any(p.is_symlink() or p.is_junction() for p in [scratch, *scratch.rglob('*')]):
            print('Retaining linked scratch: '+str(scratch), file=sys.stderr)
        else:
            shutil.rmtree(scratch)
    return 0 if report['reward'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
