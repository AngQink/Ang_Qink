"""Starter for the multiplexed NDJSON task. See README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        c = json.loads(line)
        if c['op'].endswith('_init'):
            ans = {'ok': True}
        else:
            raise NotImplementedError('Implement five subprotocols')
        sys.stdout.buffer.write(json.dumps(ans, separators=(',', ':')).encode() + b'\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
