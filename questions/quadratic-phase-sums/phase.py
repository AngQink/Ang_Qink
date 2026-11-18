"""Implement the quadratic-phase query protocol described in README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        c=json.loads(line)
        if c['op']=='init':result={'ok':True}
        else:raise NotImplementedError('Implement README.md')
        sys.stdout.buffer.write(json.dumps(result,separators=(',',':')).encode()+b'\n');sys.stdout.buffer.flush()


if __name__=='__main__':main()
