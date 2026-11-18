"""Starter for the multiplexed NDJSON task. See README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        command = json.loads(line)
        op = command['op']
        if op.endswith('_init'):
            result = {'ok': True}
        else:
            raise NotImplementedError('Implement the two subprotocols')
        sys.stdout.buffer.write(json.dumps(result, separators=(',', ':')).encode() + b'\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
