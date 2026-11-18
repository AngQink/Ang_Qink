"""Starter for the multiplexed NDJSON task. See README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        c = json.loads(line)
        op = c['op']
        if op.endswith('_init'):
            result = {'ok': True}
        else:
            raise NotImplementedError('Implement the three subprotocols')
        sys.stdout.buffer.write(json.dumps(result, separators=(',', ':')).encode() + b'\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
