"""Implement modular affine relations here. Use UTF-8 NDJSON for input and output."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        command = json.loads(line)
        if command['op'] == 'init':
            result = {'ok': True}
        else:
            raise NotImplementedError('Implement the complete README.md protocol')
        sys.stdout.buffer.write(json.dumps(result, separators=(',', ':')).encode() + b'\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
