"""处理 NDJSON 输入和输出的答题骨架，题意见 README.md。"""
import json
import sys


def main():
    output = sys.stdout.buffer
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        command = json.loads(line)
        if command['op'] == 'query':
            raise NotImplementedError('Implement the exact fiber queries')
        output.write(b'{"ok":true}\n')
        output.flush()


if __name__ == '__main__':
    main()
