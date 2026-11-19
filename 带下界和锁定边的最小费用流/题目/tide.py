"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import sys


def main():
    output = sys.stdout.buffer
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        cmd = json.loads(line)
        if cmd['op'] == 'solve':
            raise NotImplementedError('Implement solve and state transitions')
        output.write(b'{"ok":true}\n')
        output.flush()


if __name__ == '__main__':
    main()
