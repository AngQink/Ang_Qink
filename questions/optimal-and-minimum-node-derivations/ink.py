"""Implement the weighted grammar protocol described in README.md."""
import json
import sys


def main():
    for line in sys.stdin.buffer:
        command = json.loads(line)
        if command['op'] == 'init':
            result = {'ok': True}
        else:
            raise NotImplementedError('Implement SPEC.md')
        sys.stdout.buffer.write(json.dumps(result, separators=(',', ':')).encode() + b'\n')
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
